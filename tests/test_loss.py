import os
import unittest

import numpy as np
import pandas as pd
import torch

from avae.loss import AVAELoss
from avae.model_a import AffinityVAE as avae_a
from avae.utils import set_device
from tests import testdata

torch.manual_seed(0)


class LossTest(unittest.TestCase):
    def setUp(self) -> None:
        """Test instantiation of the loss."""

        self._orig_dir = os.getcwd()
        self.test_data = os.path.dirname(testdata.__file__)
        os.chdir(self.test_data)

        self.affinity = pd.read_csv("affinity_fsc_10.csv").to_numpy(
            dtype=np.float32
        )
        self.loss = AVAELoss(
            torch.device("cpu"),
            [1],
            [1],
            lookup_aff=self.affinity,
            recon_fn="MSE",
        )
        self.vae_a = avae_a(
            capacity=8,
            depth=4,
            input_size=(64, 64, 64),
            latent_dims=16,
            pose_dims=3,
        )
        self.device = set_device(True)

    def tearDown(self):
        os.chdir(self._orig_dir)

    def test_loss_instatiation(self):
        """Test instantiation of the loss."""

        assert isinstance(self.loss, AVAELoss)

    def test_loss(self):

        x = torch.randn(14, 1, 64, 64, 64)

        x_hat, lat_mu, lat_logvar, lat, lat_pose = self.vae_a(x)
        total_loss, recon_loss, kldivergence, affin_loss = self.loss(
            x,
            x_hat,
            lat_mu,
            lat_logvar,
            0,
            batch_aff=torch.ones(14, dtype=torch.int),
        )

        self.assertGreaterEqual(total_loss.detach().numpy().item(0), 1.1171)
        self.assertGreater(recon_loss.detach().numpy().item(0), 1)
        self.assertGreater(recon_loss, kldivergence)
        self.assertGreater(total_loss, affin_loss)
