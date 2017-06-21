
from datetime import datetime
import csv

from seqmod.misc.loggers import Logger


class CSVLogger(Logger):
    """
    CSV logger to record model parametres and loss info per epoch.

    """
    def __init__(self, args=None, save_path=None):
        self.args = args
        self.save_path = save_path
        self.note = args.note

    def store(self, save_path, payload):
        print("Saving to: ", save_path)
        epoch_info = self.payload_wrapper(payload)

        if payload['epoch'] == 1:
            # Get the model header and entries from arsparse
            head, args = zip(*vars(self.args).items())

            # Epoch info
            # Save it as a line in the CSV
            epoch_header = ['Date', 'Epoch', "Loss"]

            # Write a new line of model info
            with open(save_path, 'a+') as f:
                writer = csv.writer(f)
                writer.writerows([self.args.note])
                writer.writerows([head, args])
                writer.writerows([epoch_header, epoch_info])
        else:
            with open(save_path, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(epoch_info)

    def payload_wrapper(self, payload):
        '''
        Wrap up the 'per-event' data
        '''
        # Performance Metrics
        date = str(datetime.now())
        e = payload['epoch']
        l = payload['loss']['loss']

        wrapped = [date, e, l]
        return wrapped

    def validation_end(self, payload):
        self.store(self.save_path, payload)
