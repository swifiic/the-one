/*
 * Copyright 2010 Aalto University, ComNet
 * Released under GPLv3. See LICENSE.txt for details.
 */
package routing.vectors;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Random; 

import core.Connection;
import core.DTNHost;
import core.DTNSim;
import core.Message;
import core.MessageListener;
import core.Settings;
import core.SimClock;
import routing.MessageRouter;

/**
 * Implementation of Spray and wait router as depicted in
 * <I>Spray and Wait: An Efficient Routing Scheme for Intermittently
 * Connected Mobile Networks</I> by Thrasyvoulos Spyropoulus et al.
 * 
 * Extended for Vectors to support Video Flow: Both adaptive and non-adaptive
 *
 */
public class SNWAdaptiveRouter extends routing.ActiveRouter {
	/** identifier for the initial number of copies setting ({@value})*/
	public static final String NROF_COPIES = "nrofCopies";
	/** identifier for the binary-mode setting ({@value})*/
	public static final String BINARY_MODE = "binaryMode";
	/** SprayAndWait router's settings name space ({@value})*/
	public static final String SNWAR_NS = "SNWRtr";
	/** Message property key */
	public static final String MSG_COUNT_PROPERTY = SNWAR_NS + "." +
		"copies";
	
	public static final String ADAPTATION_MODE = "adaptMode";
	
	public static final String RNG_SEED = "rngSeed";


	/** Message generation properties */
	public static final String BURST_DURATION = "burstGap";
	public static final String CHUNK_SIZE = "burstSize";
	public static final String SVC_LAYER_SIZES_MIN = "layersSizeMin";
	public static final String SVC_LAYER_SIZES_MAX = "layersSizeMax";
	public static final String SRC_NODE = "src";
	public static final String DST_NODE = "dst";
	
	static {
		DTNSim.registerForReset(SNWAdaptiveRouter.class.getCanonicalName());
		reset();
	}
	

	protected static boolean isBinary;
	
	protected static int burstGap = Integer.MAX_VALUE;
	protected static int burstSizeMin, burstSizeMax;
	protected static int numLayers;
	protected static int layerSizesMin[], layerSizesMax[];
	protected static int nrOfCopies[];
	protected static String srcNodeName, dstNodeName;
	protected static int adaptMode; // 0 => no Adapt; 1 => Src Adapt; 2 => intermediate Adapt
	
	protected boolean isSrc = false;
	protected boolean isDst = false;
	static DTNHost srcHost=null, dstHost=null;
	static Random rng=null;

	
	public SNWAdaptiveRouter(Settings s) {
		super(s);
		Settings snwSettings = new Settings(SNWAR_NS);

		isBinary = snwSettings.getBoolean( BINARY_MODE);

		if(burstGap == Integer.MAX_VALUE) {
			int seed = snwSettings.getInt(RNG_SEED);
			rng = new Random(seed);
			adaptMode = snwSettings.getInt(ADAPTATION_MODE, 0);
			
			int chunkSizes[] = snwSettings.getCsvInts(CHUNK_SIZE);
			assert(chunkSizes.length == 2);
			burstSizeMin = chunkSizes[0];
			burstSizeMax = chunkSizes[1];
			burstGap = snwSettings.getInt(BURST_DURATION);
			srcNodeName = snwSettings.getSetting(SRC_NODE);
			dstNodeName = snwSettings.getSetting(DST_NODE);
			nrOfCopies = snwSettings.getCsvInts(NROF_COPIES);
			layerSizesMin = snwSettings.getCsvInts(SVC_LAYER_SIZES_MIN);
			layerSizesMax = snwSettings.getCsvInts(SVC_LAYER_SIZES_MAX);
			assert(layerSizesMin.length == layerSizesMax.length);
			numLayers = layerSizesMin.length;
			System.out.println("BG=" + burstGap + " adaptMode=" + adaptMode +
					" layerSizes-Len=" + layerSizesMin.length +
					"  burstmin=" + burstSizeMin + " burstax=" + burstSizeMax +
					" src=" + srcNodeName + " dst=" + dstNodeName + 
					" layersMin=" + snwSettings.getSetting(SVC_LAYER_SIZES_MIN) +
					" layersMax=" + snwSettings.getSetting(SVC_LAYER_SIZES_MAX));
		}
	}

	/**
	 * Copy constructor.
	 * @param r The router prototype where setting values are copied from
	 */
	protected SNWAdaptiveRouter(SNWAdaptiveRouter r) {
		super(r);
	}

	@Override
	public void init(DTNHost host, List<MessageListener> mListeners) {
		super.init(host, mListeners);
		if(host.toString().equals(srcNodeName)) {
			System.out.println("Set source " + srcNodeName);
			isSrc = true;
			assert null != srcHost:  "SRC Host already set";
			srcHost = host;
		}
		if(host.toString().equals(dstNodeName)) {
			System.out.println("Set destination " + dstNodeName);
			isDst = true;
			assert null != dstHost:  "DST Host already set";
			dstHost = host;
		}
		
	}

	@Override
	public Message messageTransferred(String id, DTNHost from) {
		Message msg = super.messageTransferred(id, from);
		Integer nrofCopies = (Integer)msg.getProperty(MSG_COUNT_PROPERTY);

		assert nrofCopies != null : "Not a SnW message: " + msg;

		if (isBinary) {
			/* in binary S'n'W the receiving node gets floor(n/2) copies */
			nrofCopies = (int)Math.floor(nrofCopies/2.0);
		}
		else {
			/* in standard S'n'W the receiving node gets only single copy */
			nrofCopies = 1;
		}

		msg.updateProperty(MSG_COUNT_PROPERTY, nrofCopies);
		if (msg.getTo() == getHost()) {
			if(isDst) 
				processAtDest(msg);
			else 
				System.out.println("Message received by destination that is not identfied as isDst " + msg);
		}
		return msg;
	}

	@Override
	public boolean createNewMessage(Message msg) {
		makeRoomForNewMessage(msg.getSize());

		msg.setTtl(this.msgTtl);
		addToMessages(msg, true);
		return true;
	}

	int lastBurstTime=-3600 * 12;
	int summaryPrintTime= 0;
	@Override
	public void update() {
		super.update();
		if(isSrc) {
			if(SimClock.getIntTime() > lastBurstTime + burstGap) {
				sendBurst();
				lastBurstTime = SimClock.getIntTime();
			}
			if(summaryPrintTime + 12 * 3600 < SimClock.getIntTime()) {
				summaryPrintTime = SimClock.getIntTime();
				printSummary();
			}
		}
		
		if (!canStartTransfer() || isTransferring()) {
			return; // nothing to transfer or is currently transferring
		}

		/* try messages that could be delivered to final recipient */
		if (exchangeDeliverableMessages() != null) {
			return;
		}

		/* create a list of SAWMessages that have copies left to distribute */
		@SuppressWarnings(value = "unchecked")
		List<Message> copiesLeft = sortByQueueMode(getMessagesWithCopiesLeft());

		if (copiesLeft.size() > 0) {
			/* try to send those messages */
			this.tryMessagesToConnections(copiesLeft, getConnections());
		}
	}

	/**
	 * Creates and returns a list of messages this router is currently
	 * carrying and still has copies left to distribute (nrof copies > 1).
	 * @return A list of messages that have copies left
	 */
	protected List<Message> getMessagesWithCopiesLeft() {
		List<Message> list = new ArrayList<Message>();

		for (Message m : getMessageCollection()) {
			Integer nrofCopies = (Integer)m.getProperty(MSG_COUNT_PROPERTY);
			assert nrofCopies != null : "SnW message " + m + " didn't have " +
				"nrof copies property!";
			if (nrofCopies > 1) {
				list.add(m);
			}
		}

		return list;
	}

	/**
	 * Called just before a transfer is finalized (by
	 * {@link ActiveRouter#update()}).
	 * Reduces the number of copies we have left for a message.
	 * In binary Spray and Wait, sending host is left with floor(n/2) copies,
	 * but in standard mode, nrof copies left is reduced by one.
	 */
	@Override
	protected void transferDone(Connection con) {
		Integer nrofCopies;
		String msgId = con.getMessage().getId();
		/* get this router's copy of the message */
		Message msg = getMessage(msgId);

		if (msg == null) { // message has been dropped from the buffer after..
			return; // ..start of transfer -> no need to reduce amount of copies
		}

		/* reduce the amount of copies left */
		nrofCopies = (Integer)msg.getProperty(MSG_COUNT_PROPERTY);
		if (isBinary) {
			/* in binary S'n'W the sending node keeps ceil(n/2) copies */
			nrofCopies = (int)Math.ceil(nrofCopies/2.0);
		}
		else {
			nrofCopies--;
		}
		msg.updateProperty(MSG_COUNT_PROPERTY, nrofCopies);
	}

	@Override
	public void changedConnection(Connection con) {
		super.changedConnection(con);
		if (con.isUp() ) {
			importAcks(con.getOtherNode(getHost()).getRouter());
		}
	}
	

	@Override
	public SNWAdaptiveRouter replicate() {
		return new SNWAdaptiveRouter(this);
	}
	
	/**
	 * Reset the settings for next simulation run
	 */
	public static void reset() {
		burstGap = Integer.MAX_VALUE;
		srcHost=null;
		dstHost=null;
		Settings s = new Settings(SNWAR_NS);
		if (s.contains(RNG_SEED)) {
			int seed = s.getInt(RNG_SEED);
			rng = new Random(seed);
		}
		else {
			rng = new Random(0);
		}
	}

	// from script copyCounts=( 768,512,256,256,192,192,128,128,96,96 
	int burstId =0;
	int sentCount = 0;
	protected void sendBurst() {
		assert null != srcHost : "SRC host not set";
		assert null != dstHost : "DST host not set";
		assert rng !=null : "rngSeed not set for SNWAdaptiveRtr";
		for(int i =0; i < numLayers; i++) {
			String msgId = "B" + String.format("%04d", burstId) + "_L" + i;
			int size = layerSizesMin[i] + (int)((layerSizesMax[i] - layerSizesMin[i]) * rng.nextDouble());
			Message m = new Message(srcHost, dstHost, msgId, size);
			int copyCount = nrOfCopies[i];// TODO logic for adaptive mode
			m.addProperty(MSG_COUNT_PROPERTY, new Integer(copyCount)); 
			
			this.createNewMessage(m);
			sentCount++;
			if(sentCount < 40 || sentCount %500 ==0) {
				System.out.println("Sent message with ID " + m.getId() +
						           " for a total of " + sentCount);
			}
		}
		burstId++;
	}
	
	List<String> ackList = new ArrayList<String>();
	List<String> srcAckList = new ArrayList<String>();
	static int removalCount = 0;
	protected void importAcks(MessageRouter other) {
		int incomingSize = ackList.size();
		try {
			SNWAdaptiveRouter oth = (SNWAdaptiveRouter)other;
			List<String> otherList = oth.ackList;
			for(String msgId : otherList) {
				if(isSrc) { // for source a private variable to keep all acks
					if(!srcAckList.contains(msgId))
						srcAckList.add(msgId);
				}
				if(ackList.contains(msgId)) continue;
				ackList.add(msgId);
				if(this.getMessage(msgId) != null) {
					this.deleteMessage(msgId, false); // not a buffer full drop
					if(removalCount++ < 100 || removalCount %1000 == 0)
						System.out.println("Deleted on ack at node " + 
					                       getHost() + " total deleted " + removalCount);
				}
			}
			Collections.sort(ackList);
		}catch (Exception ex) {
			assert false : "Failed to merge from other router" + ex.getMessage();
		}
		
		if(incomingSize > ackList.size() ) {
			// can log the additional inputs
			while(ackList.size() > 4096) {
				ackList.remove(0);
			}
		}

	}
	
	int destRcvdCount =0;
	protected void processAtDest(Message m) {
		ackList.add(m.getId());
		destRcvdCount++;
		if(destRcvdCount < 100 || destRcvdCount %500 ==0)
		System.out.println("Delivered at destination " + m.getId() + " count=" + destRcvdCount);
	}

	void 	printSummary() {
		System.out.println("At time " + SimClock.getIntTime() / 3600 + " hours Sent=" + sentCount + 
				" delivered=" + ((SNWAdaptiveRouter)dstHost.getRouter()).destRcvdCount);
	}
}
