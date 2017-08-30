# -*- coding: utf-8 -*-
"""
Loading modules from a string representing the class name
or a short name that matches the dictionary item defined
in this module
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import importlib

import tensorflow as tf

from niftynet.utilities.util_common import \
    _damerau_levenshtein_distance as edit_distance

# pylint: disable=too-few-public-methods
SUPPORTED_APP = {
    'net_regress':
        'niftynet.application.regression_application.RegressionApplication',
    'net_segment':
        'niftynet.application.segmentation_application.SegmentationApplication',
    'net_autoencoder':
        'niftynet.application.autoencoder_application.AutoencoderApplication',
    'net_gan':
        'niftynet.application.gan_application.GANApplication',
}

SUPPORTED_NETWORK = {
    # GAN
    'simulator_gan':
        'niftynet.network.simulator_gan.SimulatorGAN',
    'simple_gan':
        'niftynet.network.simple_gan.SimpleGAN',

    # Segmentation
    "highres3dnet":
        'niftynet.network.highres3dnet.HighRes3DNet',
    "highres3dnet_small":
        'niftynet.network.highres3dnet_small.HighRes3DNetSmall',
    "highres3dnet_large":
        'niftynet.network.highres3dnet_large.HighRes3DNetLarge',
    "toynet":
        'niftynet.network.toynet.ToyNet',
    "unet":
        'niftynet.network.unet.UNet3D',
    "vnet":
        'niftynet.network.vnet.VNet',
    "dense_vnet":
        'niftynet.network.dense_vnet.DenseVNet',
    "deepmedic":
        'niftynet.network.deepmedic.DeepMedic',
    "scalenet":
        'niftynet.network.scalenet.ScaleNet',
    "holistic_scalenet":
        'niftynet.network.holistic_scalenet.HolisticScaleNet',

    # autoencoder
    "vae": 'niftynet.network.vae.VAE'
}

SUPPORTED_LOSS_GAN = {
    'CrossEntropy': 'niftynet.layer.loss_gan.cross_entropy',
}

SUPPORTED_LOSS_SEGMENTATION = {
    "CrossEntropy":
        'niftynet.layer.loss_segmentation.cross_entropy',
    "Dice":
        'niftynet.layer.loss_segmentation.dice',
    "Dice_NS":
        'niftynet.layer.loss_segmentation.dice_nosquare',
    "GDSC":
        'niftynet.layer.loss_segmentation.generalised_dice_loss',
    "WGDL":
        'niftynet.layer.loss_segmentation.wasserstein_generalised_dice_loss',
    "SensSpec":
        'niftynet.layer.loss_segmentation.sensitivity_specificity_loss',
    "L1Loss":
        'niftynet.layer.loss_segmentation.l1_loss',
    "L2Loss":
        'niftynet.layer.loss_segmentation.l2_loss',
    "Huber":
        'niftynet.layer.loss_segmentation.huber_loss'
}


SUPPORTED_LOSS_REGRESSION = {
    "L1Loss":
        'niftynet.layer.loss_regression.l1_loss',
    "L2Loss":
        'niftynet.layer.loss_regression.l2_loss',
    "MSE":
        'niftynet.layer.loss_regression.mse_loss',
    "Huber":
        'niftynet.layer.loss_regression.huber_loss'
}

SUPPORTED_LOSS_AUTOENCODER = {
    "VariationalLowerBound":
        'niftynet.layer.loss_autoencoder.variational_lower_bound',
}

SUPPORTED_OPTIMIZERS = {
    'adam': 'niftynet.engine.application_optimiser.Adam',
    'gradientdescent': 'niftynet.engine.application_optimiser.GradientDescent',
    'momentum': 'niftynet.engine.application_optimiser.Momentum',
    'adagrad': 'niftynet.engine.application_optimiser.Adagrad',
}


def select_module(module_name, type_str, lookup_table):
    module_name = '{}'.format(module_name)
    if module_name in lookup_table:
        module_name = lookup_table[module_name]
    module, class_name = None, None
    try:
        module, class_name = module_name.rsplit('.', 1)
        the_module = getattr(importlib.import_module(module), class_name)
        return the_module
    except (AttributeError, ValueError):
        # Two possibilities: a typo for a lookup table entry
        #                 or a non-existing module
        dists = {k: edit_distance(k, module_name) for k in lookup_table.keys()}
        closest = min(dists, key=dists.get)
        if dists[closest] <= 3:
            err = 'Could not import {2}: By "{0}", ' \
                  'did you mean "{1}"?\n "{0}" is ' \
                  'not a valid option. '.format(module_name, closest, type_str)
            tf.logging.fatal(err)
            raise ValueError(err)
        else:
            if '.' not in module_name:
                err = 'Could not import {}: ' \
                      'Incorrect module name format {}. ' \
                      'Expected "module.object".'.format(type_str, module_name)
                tf.logging.fatal(err)
                raise ValueError(err)
            err = '{}: Could not import object' \
                  '"{}" from "{}"'.format(type_str, class_name, module)
            tf.logging.fatal(err)
            raise ValueError(err)


class ModuleFactory(object):
    SUPPORTED = None
    type_str = 'object'

    @classmethod
    def create(cls, name):
        return select_module(name, cls.type_str, cls.SUPPORTED)


class ApplicationNetFactory(ModuleFactory):
    SUPPORTED = SUPPORTED_NETWORK
    type_str = 'network'


class ApplicationFactory(ModuleFactory):
    SUPPORTED = SUPPORTED_APP
    type_str = 'application'


class LossGANFactory(ModuleFactory):
    SUPPORTED = SUPPORTED_LOSS_GAN
    type_str = 'GAN loss'


class LossSegmentationFactory(ModuleFactory):
    SUPPORTED = SUPPORTED_LOSS_SEGMENTATION
    type_str = 'segmentation loss'


class LossRegressionFactory(ModuleFactory):
    SUPPORTED = SUPPORTED_LOSS_REGRESSION
    type_str = 'regression loss'


class LossAutoencoderFactory(ModuleFactory):
    SUPPORTED = SUPPORTED_LOSS_AUTOENCODER
    type_str = 'autoencoder loss'


class OptimiserFactory(ModuleFactory):
    SUPPORTED = SUPPORTED_OPTIMIZERS
    type_str = 'optimizer'
