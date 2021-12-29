"""
This file indetify the Pallet moves to detect the Mate/Unmate Events and save data to database
"""
from models.pallet import PalletModel
from models.forklift import ForkliftModel
from managers.pallet_manager import PalletManager
from managers.forklift_manager import ForkliftManager
from managers.fnp_manager import FNPManager


class PalletMoves:
    """
    This class creates the Managers objects, read the messsages from the service bus and detect the mate/unmate events
    """
    def __init__(self):
        self.pallet_manager = PalletManager(None, None, None)
        self.forklift_manager = ForkliftManager(None)
        self.fnp_manager = FNPManager(self.pallet_manager, self.forklift_manager, None, None, None)
        print(self.pallet_manager.tracked_pallets)
        self.running_thread = False
        self.camera_metadata = {}      # camera meta info

    def message_thread(self, messages):
        """
        Put all the messages into it's specific camera queues
        :param messages: list of all messages
        """
        index = 0
        while index < len(messages) and self.running_thread:
            try:
                message = messages[index]
                camera_name = message["sensor"]
                self.camera_metadata[camera_name]["queue"].put(message)
                index += 1
            except Exception as e:
                print(e)
                index += 1


if __name__ == '__main__':
    p = PalletMoves()
    p.message_thread(None)

