import matplotlib.pyplot as plt
import numpy as np

def show_images(images=None,z=None,n_cols=2):
  n=images.shape[0]
  n_rows=n//n_cols+1
  plt.figure(figsize=(n_cols*4,n_rows*4))
  count=0
  for row in range(n_rows):
    for col in range(n_cols):
      count+=1
      if count<=n:
        plt.subplot(n_rows,n_cols,count)
        plt.imshow(images[count-1])
        plt.title(z[count-1])
  plt.show()
