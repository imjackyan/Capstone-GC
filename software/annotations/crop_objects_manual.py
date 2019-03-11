# Important: only use jpg images

import os
from collections import OrderedDict

from copy import deepcopy

from tkinter import *
from PIL import ImageTk, Image


def record_boundary(imagepath, savefolder, imagename, maxsize=(480, 480)):
    click_tracker = {
        'c': 0,
        'click0': None,
        'click1': None,
        'clicks': [],
        'cid': None
    }
    boundaries = []

    def clear_callback(event):
        if click_tracker['c'] == 0:
            return

        print('Clearing canvas')
        for cid in click_tracker['cid']:
            canvas.after(20, canvas.delete, cid)

        if click_tracker['c'] % 2 == 0:
            click_tracker['c'] -= 2
            if click_tracker['clicks']:
                click_tracker['clicks'].pop()
            if boundaries:
                boundaries.pop()
        else:
            click_tracker['c'] -= 1

    def click_callback_obj(event, object_name='can', color='red'):
        print("clicked at", event.x, event.y)
        c = click_tracker['c']

        if c % 2 == 0:
            assert click_tracker['click0'] is None
            click_tracker['click0'] = (event.x, event.y)

            cid0 = canvas.create_line(event.x-4, event.y-4, event.x+4, event.y+4,
                                      fill=color)
            click_tracker['cid'] = [cid0, ]
        elif c % 2 == 1:
            assert click_tracker['click1'] is None
            click_tracker['click1'] = (event.x, event.y)
            click_tracker['clicks'].append({
                'click0': click_tracker['click0'],
                'click1': click_tracker['click1']
            })

            left_boundary = min(click_tracker['click0'][0], click_tracker['click1'][0])
            right_boundary = max(click_tracker['click0'][0], click_tracker['click1'][0])
            top_boundary = min(click_tracker['click0'][1], click_tracker['click1'][1])
            bottom_boundary = max(click_tracker['click0'][1], click_tracker['click1'][1])
            h = bottom_boundary - top_boundary
            w = right_boundary - left_boundary

            click_tracker['click0'] = None
            click_tracker['click1'] = None

            boundary = {
                'object_name': object_name,
                'l': left_boundary,
                'r': right_boundary,
                't': top_boundary,
                'b': bottom_boundary,
                'h': h,
                'w': w
            }
            boundaries.append(boundary)

            dash = (6, 6)

            # Reference canvas here works, even though declared further down in outer scope
            cid1 = canvas.create_line(left_boundary, top_boundary, right_boundary, top_boundary,
                                      fill=color, dash=dash)
            cid2 = canvas.create_line(left_boundary, bottom_boundary, right_boundary, bottom_boundary,
                                      fill=color, dash=dash)
            cid3 = canvas.create_line(left_boundary, top_boundary, left_boundary, bottom_boundary,
                                      fill=color, dash=dash)
            cid4 = canvas.create_line(right_boundary, top_boundary, right_boundary, bottom_boundary,
                                      fill=color, dash=dash)

            # click_tracker['cid'] =(cid1, cid2, cid3, cid4)
            click_tracker['cid'].append(cid1)
            click_tracker['cid'].append(cid2)
            click_tracker['cid'].append(cid3)
            click_tracker['cid'].append(cid4)

        click_tracker['c'] += 1

    root = Tk()
    try:
        # https://stackoverflow.com/questions/40137813/attributeerror-when-creating-tkinter-photoimage-object-with-pil-imagetk
        # open image
        image = Image.open(imagepath)
        image_size = tuple([c for c in image.size])
        x, y = image_size

        if x > maxsize[0] or y > maxsize[1]:
            r = max(x/maxsize[0], y/maxsize[1])
            x = int(x // r)
            y = int(y // r)
            print(x, y, r)

            image = image.resize((x, y), Image.ANTIALIAS)

        canvas = Canvas(root, width=x, height=y, relief=RAISED, cursor="crosshair")
        canvas.grid(row=0, column=0)
        tk_image = ImageTk.PhotoImage(image)
        image_on_canvas = canvas.create_image(0, 0, anchor=NW, image=tk_image)

        # img = ImageTk.PhotoImage(image)
        # panel = Label(root, image=tk_image)
        # panel.bind("<Button-1>", click_callback)
        # panel.pack(side="bottom", fill="both", expand="yes")
        # canvas.bind("-", lambda event: canvas.focus_set())
        click_callback_can = lambda event: click_callback_obj(event, object_name='can', color='red')
        click_callback_logo = lambda event: click_callback_obj(event, object_name='logo', color='blue')

        # Right click
        canvas.bind("<Button-1>", click_callback_can)
        # Middle click
        canvas.bind("<Button-2>", clear_callback)
        # Left click
        canvas.bind("<Button-3>", click_callback_logo)
        root.mainloop()

        # crop = image.crop((boundary['l'], boundary['t'], boundary['r'], boundary['b']))
        # crop.save(os.path.join(savefolder, str(count)), format='png')
        if boundaries:
            imagepath = os.path.join(savefolder, imagename)
            image = image.convert('L')
            image.save(imagepath)

    except FileNotFoundError as fe:
        print('[record_boundary]: FileNotFoundError', fe)
        return None

    width = x
    height = y

    return boundaries, imagepath, width, height

def is_image_file(imagename):
    return imagename.endswith('jpg') or imagename.endswith('jpeg') or imagename.endswith('png') \
        or imagename.endswith('JPG') or imagename.endswith('JPEG') or imagename.endswith('PNG') \
        or imagename.endswith('gif') or imagename.endswith('GIF')

def identify_object_boundaries(imagefolder, savefolder, samplesfile, statefile, xmlfolder):

    imagefilenames = os.listdir(imagefolder)
    # imagefilenames = set((imagename for imagename in imagefilenames if len(imagename) > 4 and imagename[-4:] == '.jpg'))
    temp = OrderedDict()
    for imagename in imagefilenames:
        if is_image_file(imagename):
            temp[imagename] = None
    imagefilenames = temp
    print('Imagefilenames:')
    print(imagefilenames)

    with open(statefile, 'r') as f2:
        labelled_images = f2.readlines()
        labelled_images = [labelled_image.strip() for labelled_image in labelled_images]
    if len(labelled_images) > 1 and not labelled_images[-1].strip():
        labelled_images.pop()

    print('labelled_images:')
    print(labelled_images)

    with open(samplesfile, 'w') as f1:
        for labelled_image in labelled_images:
            labelled_image = labelled_image.strip()
            labelled_imagefile = labelled_image + '.jpg'
            if labelled_image in labelled_images:
                print('Already done labelling (no folder prefix):', labelled_imagefile)
                # labelled_imagefile_nofolder = labelled_imagefile[len(imagefolder)+1:] # Way too confusing, fix in future
                labelled_imagefile_nofolder = labelled_imagefile
                imagefilenames.pop(labelled_imagefile_nofolder, None)
                print(labelled_imagefile_nofolder, labelled_imagefile_nofolder in imagefilenames)
            f1.write(labelled_image + '\n')

    for imagename, _ in imagefilenames.items():
        imagename = imagename.strip()
        # imageid = '%s-%s' % (imagefolder, imagename) # This is the name used to save the image
        imagepath = os.path.join(imagefolder, imagename) # This path opens the image from folder
        if not imagepath: continue

        boundaries, imagepath, width, height = record_boundary(imagepath, savefolder, imagename)
        print(boundaries)
        print(imagepath)
        if not boundaries:
            continue

        folder_imagename_noext = '.'.join(imagename.split('.')[:-1])
        with open(samplesfile, 'a') as f1, open(statefile, 'a') as f2:
            f1.write(folder_imagename_noext + '\n')
            f2.write(folder_imagename_noext + '\n')

        xmlfile = folder_imagename_noext + '.xml'
        with open(os.path.join(xmlfolder, xmlfile), 'w') as f3:
            f3.write('<annotation>\n')
            f3.write('\t<folder>less_selected</folder>\n')
            f3.write('\t<filename>%s</filename>\n' % (imagename,))
            f3.write('\t<size>\n')
            f3.write('\t\t<width>%d</width>\n' % (width,))
            f3.write('\t\t<height>%d</height>\n' % (height,))
            f3.write('\t</size>\n')
            f3.write('\t<segmented>0</segmented>\n')
            for boundary in boundaries:
                f3.write('\t<object>\n')
                f3.write('\t\t<name>%s</name>\n' % (boundary['object_name'],))
                f3.write('\t\t<bndbox>\n')
                f3.write('\t\t\t<xmin>%d</xmin>\n' % (boundary['l'],))
                f3.write('\t\t\t<ymin>%d</ymin>\n' % (boundary['t'],))
                f3.write('\t\t\t<xmax>%d</xmax>\n' % (boundary['r'],))
                f3.write('\t\t\t<ymax>%d</ymax>\n' % (boundary['b'],))
                f3.write('\t\t</bndbox>\n')
                f3.write('\t</object>\n')
            f3.write('</annotation>\n')

    return


if __name__ == '__main__':
    imagefolder = 'td5'
    savefolder = 'images'
    samplesfile = 'annotations/trainval.txt'
    # same as samplesfile, but with file extension so set operations can be performed
    statefile = 'annotations/state.txt'
    xmlfolder = 'annotations/xmls'

    # with open(samplesfile, 'w') as f:
    #     for imagepath in imagepaths:
    #         f.write(imagepath + '\n')

    identify_object_boundaries(imagefolder, savefolder, samplesfile, statefile, xmlfolder)
