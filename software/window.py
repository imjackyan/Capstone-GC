from PIL import Image, ImageTk, ImageDraw
import sys
import tkinter as tk

# c = Client()


class Window():
	def __init__(self):
		self.window = tk.Tk()
		self.window.title("Monitor")
		self.label = None

	def rectangle(self, PIL_img, coord, thickness = 3):
		# coord is a tuple of tuples ((x1,y1), (x2, y2))
		clr = 'green'
		draw = ImageDraw.Draw(PIL_img)
		draw.rectangle((coord[0], (coord[0][0] + thickness, coord[1][1])), fill = clr)
		draw.rectangle((coord[0], (coord[1][0], coord[0][1] + thickness)), fill = clr)
		draw.rectangle(((coord[1][0] - thickness, coord[0][1]), coord[1]), fill = clr)
		draw.rectangle(((coord[0][0], coord[1][1] - thickness), coord[1]), fill = clr)

	def display(self, PIL_img):
		self.img = ImageTk.PhotoImage(PIL_img)

		if self.label is None:
			self.label = tk.Label(self.window, image = self.img)
			self.label.pack(side = tk.TOP , fill = tk.BOTH, expand = tk.YES)
			self.window.update()

		self.window.geometry("%dx%d" % (self.img.width(), self.img.height()))
		self.label.configure(image = self.img)
		self.window.update()
	def update(self):
		self.window.update()
	def destroy(self):
		self.window.destroy()


if __name__ == '__main__':
	w = Window()
	i = Image.open("positive-16.jpg")

	w.rectangle(i, ((50,0), (100,100)))

	w.display(i)


	input("as")

	w.display(Image.open("positive-15.jpg"))
	input("as")
