import numpy as np

def rainbow2gray(image,mapvals_dir):
  mapvals=np.load(mapvals_dir,allow_pickle=True)
  r = np.linspace(0,1, 256)
  newim = np.zeros((image.shape[0],image.shape[1]),dtype='uint8')
  for i in range(image.shape[0]):
      for j in range(image.shape[1]):
          c = image[i,j,:3]
          c=c.astype('float32')/255.0
          gray=r[np.argmin(np.sum((mapvals - c)**2, axis=1))]
          newim[i,j] =  np.round(255.0*gray).astype('uint8')
  return newim

def gray2rainbow(gray,mapvals_dir):
  mapvals=np.load(mapvals_dir,allow_pickle=True)
  rainbow=np.zeros((gray.shape[0],gray.shape[1],3),'float32')
  for i in range(gray.shape[0]):
    for j in range(gray.shape[1]):
      rainbow[i,j,:]=mapvals[gray[i,j]]
  return (255*rainbow).astype('uint8') 


def gray2rainbow_batch(ims,mapvals_dir): #(batch_size,1,64,64)
  rainbow=[]
  for i in range(ims.shape[0]):
    rainbow.append(gray2rainbow(ims[i],mapvals_dir))
  return np.array(rainbow) 
