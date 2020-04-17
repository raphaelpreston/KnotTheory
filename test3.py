from PyQt5.QtWidgets import QMainWindow, QLabel, QSizePolicy, QApplication 
from PyQt5.QtGui import QPixmap, QImage                                
from PyQt5.QtCore import Qt                                                                                              
import numpy as np                                                     
import sys
from skimage import io, color, morphology, img_as_float



class Test(QMainWindow):                                                                                                                                                                                       

    def __init__(self):                                                                                                                                                                                        
        super().__init__()                                                                                                                                                                                     
        self.initUI()                                                                                                                                                                                          

    def initUI(self):                                                                                                                                                                                          
        self.setGeometry(10,10,640, 400)                                                                                                                                                                       

        pixmap_label = QLabel()                                                                                                                                                                                
        pixmap_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)                                                                                                                                   
        pixmap_label.resize(640,400)                                                                                                                                                                           
        pixmap_label.setAlignment(Qt.AlignCenter)                                                                                                                                                              

        
        # old_np = np.ones((300,100,3),dtype=np.uint8)                                                                                                                                                                                  
        # height, width, _ = self.imageData.shape
        im_np = np.require(io.imread("knot1.png"), np.uint8, 'C')
        # im_np = np.ones((300,100,3),dtype=np.uint8)
        # for row in im_np:
        #     for col in im_np:
        #         for pix in col:
        #             pix = [255, 255, 255]

        im_np = np.transpose(im_np, (1,0,2))
        im_np = np.transpose(im_np,(1,0,2)).copy()
                                                                                                                                                                                
        qimage = QImage(im_np, im_np.shape[1], im_np.shape[0], QImage.Format_RGB888)                                                                                                                                                                 
        pixmap = QPixmap(qimage)                                                                                                                                                                               
        pixmap = pixmap.scaled(640,400, Qt.KeepAspectRatio)                                                                                                                                                    
        pixmap_label.setPixmap(pixmap)                                                                                                                                                                         

        self.setCentralWidget(pixmap_label)                                                                                                                                                                    
        self.show()                                                                                                                                                                                            

def main():                                                                                                                                                                                                    
    app = QApplication(sys.argv)                                                                                                                                                                               
    win = Test()                                                                                                                                                                                               
    sys.exit(app.exec_())                                                                                                                                                                                      

if __name__=="__main__":                                                                                                                                                                                       
  main()  