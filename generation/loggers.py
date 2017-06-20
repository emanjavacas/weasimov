# from visdom import Visdom

import logging
import numpy as np
import random

import torch
from torch.autograd import Variable

import os
from datetime import datetime
import csv

class Logger(object):

    def log(self, event, payload, verbose=True):
        if verbose and hasattr(self, event):
            getattr(self, event)(payload)


def loss_str(loss, phase):
    return "; ".join([phase + " %s: %g" % (k, v) for (k, v) in loss.items()])


class CSVLogger(Logger):
    """
    CSV logger to record model parametres and loss info per epoch.

    """

    def __init__(self, outputfile=None,
                 level='INFO',
                 msgfmt="[%(asctime)s] %(message)s",
                 datefmt='%m-%d %H:%M:%S',
                 args=None,
                 save_path=None,
                 model=None):
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False
        self.logger.handlers = []
        self.logger.setLevel(getattr(logging, level))
        self.args = args
        self.save_path = save_path
        self.model = model
        self.note = args.note
        formatter = logging.Formatter(msgfmt, datefmt)
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        self.logger.addHandler(sh)
        if outputfile is not None:
            fh = logging.FileHandler(outputfile)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

    def modelLogger(self):
        '''
        Save a record of the pytorch model being used.
        from 'seqmod.modules.encoder_decoder.EncoderDecoder'
        '''
        # TODO add indexing.
        opts = {k: v for k, v in vars(self.args).items()}
        
        head, args = [], []
        
        for i,k in opts.items():
            head.append(i)
            args.append(k)

        return head, args

    def store(self, save_path, payload):
        '''
        '''
        epoch_info = self.payloadWrapper(payload)
        
        if payload['epoch'] == 1:
            # Get the model header and entries from arsparse
            head, args = self.modelLogger()

            # Epoch info
            #Save it as a line in the CSV
            epoch_header = ['Date','Epoch', "Loss"]

            print("Saving to: ", save_path)

            # Check if we're reusing a file.
            if os.path.isfile(save_path):
                m = 'a'
            else:
                m = 'w'

            # Write a new line of model info
            with open(save_path, m) as f:
                writer = csv.writer(f)
                writer.writerows([self.args.note])
                writer.writerows([head, args])
                writer.writerows([epoch_header, epoch_info])
                f.close
        else:
            print("Saving to: ", save_path)
            with open(save_path, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(epoch_info)

    def payloadWrapper(self, payload):
        '''
        Wrap up the 'per-event' data
        '''
        # Performance Metrics
        date = str(datetime.now())
        e = payload['epoch']
        l = payload['loss']['loss']

        wrapped = [date, e, l]
        return wrapped

    def epoch_begin(self, payload):
        self.logger.info("Starting epoch [%d]" % payload['epoch'])

    def epoch_end(self, payload):
        speed = payload["examples"] / payload["duration"]
        loss = loss_str(payload['loss'], 'train')
        self.logger.info("Epoch [%d]; %s; speed: %d tokens/sec" %
                         (payload['epoch'], loss, speed))

    def validation_end(self, payload):
        loss = loss_str(payload['loss'], 'valid')
        self.logger.info("Epoch [%d]; %s" % (payload['epoch'], loss))
        self.store(self.save_path, payload)

    def test_begin(self, payload):
        self.logger.info("Testing...")

    def test_end(self, payload):
        self.logger.info(loss_str(payload['loss'], 'Test'))

    def checkpoint(self, payload):
        e, b, bs = payload['epoch'], payload['batch'], payload['total_batches']
        speed = payload["examples"] / payload["duration"]
        loss = loss_str(payload['loss'], 'train')
        self.logger.info("Epoch[%d]; batch [%d/%d]; %s; speed %d tokens/sec" %
                         (e, b, bs, loss, speed))

    def info(self, payload):
        if isinstance(payload, dict):
            payload = payload['message']
        self.logger.info(payload)

