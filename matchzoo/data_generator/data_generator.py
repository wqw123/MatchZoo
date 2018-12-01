"""Base generator."""

import math
import typing

import keras
import numpy as np

from matchzoo import DataPack


class DataGenerator(keras.utils.Sequence):
    """Abstract base class of all matchzoo generators.

    Every generator must implement :meth:`_get_batch_of_transformed_samples`
    method.

    Examples:
        >>> import matchzoo as mz
        >>> input = mz.datasets.toy.load_train_classify_data()
        >>> data_generator = DataGenerator(input, 1, False)
        >>> len(data_generator)
        49
        >>> data_generator.num_instance
        49
        >>> x, y = data_generator[0]
        >>> x['text_left'].tolist()
        ['How can I increase the speed of my internet connection while using a\
 VPN?']
        >>> x['text_right'].tolist()
        ['How can Internet speed be increased by hacking through DNS?']
        >>> x['id_left'].tolist()
        ['q1']
        >>> x['id_right'].tolist()
        ['d1']
        >>> y.tolist()
        [0.0]
        >>> data_generator.reset()
        >>> x1, y1 = data_generator[:2]
        >>> len(x1['text_left'])
        2
        >>> y1.tolist()
        [0.0, 1.0]
        >>> data_generator.on_epoch_end()
        >>> x2, y2 = data_generator[0:2]
        >>> y2.tolist()
        [0.0, 1.0]

    """

    def __init__(
        self,
        data_pack: DataPack,
        batch_size: int = 32,
        shuffle: bool = True
    ):
        """
        :class:`DataGenerator` constructor.

        :param data_pack: a :class:`DataPack` object.
        :param batch_size: number of instances for each batch
        :param shuffle: a bool variable to determine whether choose samples
        randomly
        """
        self._data_pack = data_pack
        self._batch_size = batch_size
        self._shuffle = shuffle

        self._batch_indices = None
        self._set_indices()

    def __getitem__(self, item: int) -> typing.Tuple[dict, list]:
        """Get a batch from index idx.

        :param item: the index of the batch.
        """
        if isinstance(item, slice):
            indices = sum(self._batch_indices[item], [])
        else:
            indices = self._batch_indices[item]
        return self._get_batch_of_transformed_samples(indices)

    def _get_batch_of_transformed_samples(
        self,
        indices: np.array
    ) -> typing.Tuple[dict, typing.Any]:
        """Get a batch of samples based on their ids.

        :param indices: a list of instance ids.
        :return: A batch of transformed samples.
        """
        return self._data_pack[indices].unpack()

    def __len__(self) -> int:
        """Get the total number of batches."""
        return math.ceil(self.num_instance / self._batch_size)

    def on_epoch_end(self):
        """Reorganize the index array while epoch is ended."""
        self._set_indices()

    def reset(self):
        """Reset the generator from begin."""
        self._set_indices()

    @property
    def num_instance(self) -> int:
        """Return the number of instances."""
        return len(self._data_pack)

    def _set_indices(self):
        """
        Set the :attr:`index_array`.

        Here the :attr:`index_array` records the index of all the instances.
        """
        if self._shuffle:
            index_pool = np.random.permutation(self.num_instance).tolist()
        else:
            index_pool = list(range(self.num_instance))
        self._batch_indices = []
        for i in range(len(self)):
            lower = self._batch_size * i
            upper = self._batch_size * (i + 1)
            self._batch_indices.append(index_pool[lower: upper])
