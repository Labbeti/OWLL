from abc import abstractmethod


class PieEventObserver:
    @abstractmethod
    def onClusterClick(self, label: str):
        """
            Event called when user lick on pie chart for displaying the OP name list.
            :param label: The label (center) of the cluster selected.
        """
        raise Exception("Not implemented")
