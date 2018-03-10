import os, time
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from model import build_model
import itertools

import generator

def timestamp():

	return time.strftime( "%Y%m%d%H%M%S", time.gmtime() )
#end timestamp

def memory_usage():
	pid=os.getpid()
	s = next( line for line in open( '/proc/{}/status'.format( pid ) ).read().splitlines() if line.startswith( 'VmSize' ) ).split()
	return "{} {}".format( s[-2], s[-1] )
#end memory_usage

if __name__ == "__main__":
	time_steps = 8
	batch_size = 8
	epochs = 100
	n = 8
	m = 8
	d = 8
	Lmsg_sizes 	= [2*n*d,	2*n*d,	2*n*d]
	Cmsg_sizes 	= [m*d, 	m*d,	m*d]
	Lvote_sizes = [32,		32,		32]
	
	# Build model
	print("Building model ...")
	M, pred_SAT, label_SAT, loss, train_step, var_dict = build_model( 
		time_steps = time_steps,
		batch_size = batch_size,
		d = d,
		n = n,
		m = m,
		Lmsg_sizes = Lmsg_sizes,
		Lvote_sizes = Lvote_sizes,
		Cmsg_sizes = Cmsg_sizes
)

	# Create batch generator
	print("Creating batch generator ...")
	generator = generator.generate(n, m, batch_size=batch_size)


	# Allow GPU memory growth
	config = tf.ConfigProto()
	config.gpu_options.per_process_gpu_memory_fraction = 0.9
	with tf.Session(config=config) as sess:
		# Initialize global variables
		print("Initializing global variables ... ")
		sess.run( tf.global_variables_initializer() )
		# Run for a number of epochs
		print("Running for {} epochs".format(epochs))
		epoch = 1
		for epoch, batch in zip( range(epochs), generator ):
			# Get features, labels
			features, labels = batch
			# Run session
			_, _, loss_val = sess.run( [train_step, pred_SAT, loss], feed_dict={M: features, label_SAT: labels} )
			# Print train step and loss
			print(
				"{timestamp}\t{memory}\tEpoch {epoch} Loss: {loss}".format(
					timestamp = timestamp(),
					memory = memory_usage(),
					epoch = epoch,
					loss = loss_val
				)
			)
		#end for
	#end with
pass
