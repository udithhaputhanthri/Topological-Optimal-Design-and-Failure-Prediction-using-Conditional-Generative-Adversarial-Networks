from torch import nn
import torch
import numpy as np
import torch


device=torch.device('cpu')

class conv_block(nn.Module):
  def __init__(self,in_channels,out_channels,kernel_size=4,stride=2,padding=1):
    super(conv_block,self).__init__()
    self.conv_block=nn.Sequential(
        nn.Conv2d(in_channels,out_channels,kernel_size,stride,padding),
        nn.LeakyReLU(0.2),
        nn.BatchNorm2d(out_channels)
    )  
  def forward(self,x):
    return self.conv_block(x)
class transconv_block(nn.Module):
  def __init__(self,in_channels,out_channels,kernel_size=4,stride=2,padding=1):
    super(transconv_block,self).__init__()
    self.transconv_block=nn.Sequential(
        nn.ConvTranspose2d(in_channels,out_channels,kernel_size,stride,padding),
        nn.ReLU(),
        nn.BatchNorm2d(out_channels)
    )
  def forward(self,x):
    return self.transconv_block(x)


class CNN(nn.Module):
  def __init__(self):
    super(CNN,self).__init__()
    self.linear=nn.Linear(2,100)
    self.cnn=nn.Sequential(
        nn.ConvTranspose2d(100,64,kernel_size=4,stride=2,padding=1),
        nn.LeakyReLU(0.2),
        nn.BatchNorm2d(64),
        nn.Dropout(0.2),

        nn.ConvTranspose2d(64,32,kernel_size=4,stride=2,padding=1),
        nn.LeakyReLU(0.2),
        nn.BatchNorm2d(32),
        nn.Dropout(0.2),

        nn.ConvTranspose2d(32,16,kernel_size=4,stride=2,padding=1),
        nn.LeakyReLU(0.2),
        nn.BatchNorm2d(16),
        nn.Dropout(0.2),
    
        nn.ConvTranspose2d(16,8,kernel_size=4,stride=2,padding=1),
        nn.LeakyReLU(0.2),
        nn.BatchNorm2d(8),
        nn.Dropout(0.2),

        nn.ConvTranspose2d(8,4,kernel_size=4,stride=2,padding=1),
        nn.LeakyReLU(0.2),
        nn.BatchNorm2d(4),
        nn.Dropout(0.2),

        nn.ConvTranspose2d(4,1,kernel_size=4,stride=2,padding=1),
    )

  def forward(self,x):
    x=x.float().to(device)
    x=x.view(-1,2)
    x=self.linear(x)
    x=x.view(-1,100,1,1)
    y=self.cnn(x)
    return y

class Generator(nn.Module):
  def __init__(self):
    super(Generator,self).__init__()
    self.for_x=nn.Sequential(
        transconv_block(1,5),
        transconv_block(5,10),
        transconv_block(10,3))
    
    self.encoder=nn.Sequential(
        conv_block(1,4),
        conv_block(4,8),
        conv_block(8,16),
        conv_block(16,32),
        conv_block(32,64,kernel_size=4, stride=1,padding=0)) #gives (1,1,64)

    self.decoder=nn.Sequential(
        transconv_block(66,64,kernel_size=4, stride=1,padding=0),
        transconv_block(64,32,kernel_size=8, stride=4,padding=2),
        transconv_block(32,16),
        transconv_block(16,8,kernel_size=8, stride=4,padding=2),
        transconv_block(8,8),
        transconv_block(8,4)
    )

    self.last=nn.ConvTranspose2d(7,1,kernel_size=4,stride=2,padding=1)

  def forward(self,x,z): #z-> labels
    x=x.view(-1,1,64,64).float()
    z=z.view(-1,2,1,1).float()
    latent=self.encoder(x) #(batch_size,64,1,1)
    Z=torch.cat([z,latent],1) #(-1,66,1,1)
    feed_x=self.for_x(x)
    before_out=torch.cat([feed_x,self.decoder(Z)],1)
    out=self.last(before_out)
    return out


class TopOpt_model():
  def __init__(self,pretrained=True, cnn_path=None, G_path=None,mapvals_dir=None):
    self.mapvals_dir=mapvals_dir
    self.cnn=CNN().eval()
    self.G=Generator().eval()
    
    if pretrained==True:
      self.cnn.load_state_dict(torch.load(cnn_path+'/weights.pth',map_location=device))
      self.G.load_state_dict(torch.load(G_path+'/G_weights.pth',map_location=device))
  def predict(self,z):
    z=torch.tensor(z)
    z=z.view(-1,2)
    gray=self.G(self.cnn(z),z)
    gray=np.clip((255*gray.squeeze(1).detach().cpu().numpy()),0,255).astype('uint8')
    #rainbow=gray2rainbow_batch(gray,self.mapvals_dir)
    return gray