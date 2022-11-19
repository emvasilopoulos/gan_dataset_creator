from editor.component import Component
from editor.components.super_resolution_srdiff_diffusion.utils.hparams import set_hparams
from editor.components.super_resolution_srdiff_diffusion.models.diffsr_modules import Unet, RRDBNet
from editor.components.super_resolution_srdiff_diffusion.models.diffusion import GaussianDiffusion
from editor.components.super_resolution_srdiff_diffusion.utils.utils import load_ckpt
import os
import importlib


class SuperResolutionSRDiff(Component):

    def edit(self, frame, *kwargs):
        pass

    def get_component_name(self) -> str:
        pass


# TODO - Need to learn how the code works. I don't understand yet.
if __name__ == '__main__':

    set_hparams('./super_resolution_srdiff_diffusion/checkpoints/srdiff_pretrained_div2k/config.yaml')
    hidden_size = 64
    dim_mults = '1|2|3|4'
    dim_mults = [int(x) for x in dim_mults.split('|')]
    denoise_fn = Unet(
        hidden_size,
        out_dim=3,
        cond_dim=32,  # ?
        dim_mults=dim_mults
    )

    rrdb = RRDBNet(3, 3, 32, 8, 32 // 2)
    rrdb = load_ckpt(rrdb, './checkpoints')

    model = GaussianDiffusion(
        denoise_fn=denoise_fn,
        rrdb_net=rrdb,
        timesteps=100,
        loss_type='l1'
    )

    pkg = ".".join('tasks.srdiff_df2k.SRDiffDf2k'.split(".")[:-1])
    cls_name = 'tasks.srdiff_df2k.SRDiffDf2k'.split(".")[-1]
    trainer = getattr(importlib.import_module(pkg), cls_name)()
    # trainer.test()
