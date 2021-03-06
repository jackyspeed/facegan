import numpy as np
import tensorflow as tf

from trainer import Trainer
from config import get_config
from data_loader import *
from utils import prepare_dirs_and_logger, save_config

def main(config):
    #if config.train_renderer:
    #    config.task = "{}_{}".format(config.task, 'ren')
    #if config.train_regressor:
    #    config.task = "{}_{}".format(config.task, 'reg')
    #    if config.pretrain_generator:
    #        config.task = "{}_{}".format(config.task, 'pregen')
    if config.train_generator:
        config.task = "{}_{}".format(config.task, 'gen')

    prepare_dirs_and_logger(config)

    rng = np.random.RandomState(config.random_seed)
    tf.set_random_seed(config.random_seed)

    if config.is_train:
        data_path = config.data_path
        batch_size = config.batch_size
        do_shuffle = True
    else:
        setattr(config, 'batch_size', 64)
        if config.test_data_path is None:
            data_path = config.data_path
        else:
            data_path = config.test_data_path
        batch_size = config.sample_per_image
        do_shuffle = False

    with tf.device('/cpu:0'):
        data_loader = get_loader(
                data_path, config.batch_size*config.num_gpu, config.input_scale_size,
                config.data_format, config)

        syn_image, syn_label, config.n_id = get_syn_loader(
                config.syn_data_dir, config.batch_size*config.num_gpu, config.syn_scale_size,
                config.data_format, config)

        image_3dmm, annot_3dmm = get_3dmm_loader(
                config.dataset_3dmm_dir, config.batch_size*config.num_gpu, config.syn_scale_size,
                config.data_format, config)

    #image_3dmm_test, annot_3dmm_test, latent_3dmm_test = get_3dmm_loader(
    #        config.dataset_3dmm_test_dir, config.batch_size, config.syn_scale_size,
    #        config.data_format, config.split)

        trainer = Trainer(config, data_loader,syn_image,syn_label, image_3dmm, annot_3dmm) #image_3dmm_test, annot_3dmm_test, latent_3dmm_test )

    if config.is_train:
        save_config(config)
        #if config.train_renderer | (config.cont == 'ren'):
        #    trainer.train_renderer()
        #if config.train_regressor | (config.cont == 'reg'):
        #    trainer.train_regressor()
        if config.train_generator | (config.cont == 'gen'):
            trainer.train()
        elif config.generate_dataset:
            trainer.generate_dataset()
        elif config.fit_dataset:
            trainer.fit_dataset()
    else:
        if not config.load_path:
            raise Exception("[!] You should specify `load_path` to load a pretrained model")
        trainer.test()

if __name__ == "__main__":
    config, unparsed = get_config()
    main(config)
