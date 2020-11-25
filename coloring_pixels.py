from PIL import Image, ImageDraw, ImageTk, ImageEnhance
import sys
from skimage import io
from sklearn.cluster import KMeans
import tkinter as tk


# GLOBAL
IMAGE_DICTIONARY = 'images/'
oryginal_image = None
oryginal_with_frames = None
TXT_LOADING1 = ('\nDownloading...', '\nFinished - 0%', '\n10%', '\n40%', '\n60%', '\n75%', '\n90%', '\n100%')
TXT_LOADING2 = ('Finished- 0%', 'Finished- {}%', '(look at toolbar)')
IMAGE_CANVAS_WIDTH, IMAGE_CANVAS_HEIGHT = 600, 600


def rgb_to_hex(rgb):
    hex_color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
    return hex_color


class IMG:
    def __init__(self):
        global oryginal_image, oryginal_with_frames

        print(TXT_LOADING1[0])

        # less colors
        less_colors = self.less_colors()

        # downloading image
        self.im = Image.fromarray(less_colors)

        # width/height
        self.width, self.height = self.im.size

        # var
        self.pixel_cords = []
        self.pixel_colors = []

        # func
        self.prepare()
        self.making_pixel_cords()
        self.making_pixel_colors()
        self.coloring_pixels()
        oryginal_with_frames = self.making_frames()     # oryginal img with frame

        # cropping image
        self.im = self.im.crop((0, 0, self.width, self.height))
        oryginal_with_frames = oryginal_with_frames.crop((0, 0, self.width, self.height))
        oryginal_image = self.im    # oryginal img wihtout frame
        oryginal_with_frames = oryginal_with_frames

    def less_colors(self):
        print(TXT_LOADING1[1])
        # less colors

        # if file exists
        try:
            original = io.imread(PATH)
        except:
            print('File not found')
            input('Press enter to quit\n')
            sys.exit()

        n_colors = HOW_MANY_COLORS

        print(TXT_LOADING1[2])

        # crop if error
        #
        try:
            arr = original.reshape((-1, 3))
        except:
            print('\n!!!\n'
                  '!!!\n'
                  'incorrect/not supported resolution!\n'
                  "the image's copy is cropped\n"
                  '!!!\n'
                  '!!!\n')

            file_name = PATH[len(IMAGE_DICTIONARY):-4]
            path_copy = IMAGE_DICTIONARY + file_name + 'CROPPED' + '.jpg'
            while True:
                imm = Image.open(PATH)
                w, h = imm.size
                imm = imm.crop((0, 0, w-1, h))
                imm = imm.convert('RGB')
                imm.save(path_copy)
                original = io.imread(path_copy)

                try:
                    arr = original.reshape((-1, 3))
                    break
                except:
                    continue
        #
        # ^^ crop if error ^^

        print(TXT_LOADING1[3])
        kmeans = KMeans(n_clusters=n_colors, random_state=42).fit(arr)
        print(TXT_LOADING1[4])
        labels = kmeans.labels_
        print(TXT_LOADING1[5])
        centers = kmeans.cluster_centers_
        print(TXT_LOADING1[6])
        less_colors = centers[labels].reshape(original.shape).astype('uint8')
        print(TXT_LOADING1[7])
        return less_colors

    def prepare(self):
        # pixel bigger than image?
        if PIXEL_SIZE > self.width or PIXEL_SIZE > self.height:
            print('Pixel size bigger than image')
            input('Press enter to quit\n')
            sys.exit()

        elif PIXEL_SIZE < 1:
            print('Pixel size smaller than 1!')
            input('Press enter to quit\n')
            sys.exit()

        # cropping few pixels
        if self.width % PIXEL_SIZE != 0:
            while self.width % PIXEL_SIZE != 0:
                self.width -= 1

        if self.height % PIXEL_SIZE != 0:
            while self.height % PIXEL_SIZE != 0:
                self.height -= 1

    def making_pixel_cords(self):
        for x in range(-PIXEL_SIZE, self.width, PIXEL_SIZE):
            x += PIXEL_SIZE
            if x == self.width:
                continue

            for y in range(-PIXEL_SIZE, self.height, PIXEL_SIZE):
                y += PIXEL_SIZE
                if y == self.height:
                    continue

                pixel = (x, y, x + PIXEL_SIZE, y + PIXEL_SIZE)
                self.pixel_cords.append(pixel)

    def making_pixel_colors(self):
        print(TXT_LOADING2[0])
        per = 0

        pix = self.im.load()

        for cords in self.pixel_cords:
            tmp_pixel_colors = []

            for i1 in range(PIXEL_SIZE):
                x = cords[0] + i1
                for i2 in range(PIXEL_SIZE):
                    y = cords[1] + i2
                    tmp_pixel_colors.append(pix[x, y])

            res = max(tmp_pixel_colors, key=tmp_pixel_colors.count)
            self.pixel_colors.append(res)

            # percents
            per_obj = self.pixel_cords.index(cords) + 1
            per_len = len(self.pixel_cords)
            if int(per_obj / per_len * 100) != per:
                per = int(per_obj / per_len * 100)
                print(TXT_LOADING2[1].format(per))
            if per == 100:
                print(TXT_LOADING2[2])

    def coloring_pixels(self):
        draw = ImageDraw.Draw(self.im)

        for i in range(len(self.pixel_cords)):
            cord = self.pixel_cords[i]
            color = self.pixel_colors[i]

            draw.rectangle(cord, color)

    def making_frames(self):
        im = self.im.copy()
        draw = ImageDraw.Draw(im)
        for cords in self.pixel_cords:
            draw.rectangle(cords)

        draw.line((0, self.height - 1, self.width - 1, self.height - 1))
        draw.line((self.width - 1, 0, self.width - 1, self.height - 1))

        return im


class GUI:
    def __init__(self, pixel_cords, pixel_colors):
        self.root = tk.Tk()

        # main frame
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack()

        # upper frame (with info)
        self.info_frame = tk.Frame(self.main_frame)
        self.info_frame.pack(side=tk.TOP)

        # canvas frame
        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(side=tk.TOP)

        # buttons frame
        self.buttons_frame = tk.Frame(self.main_frame)
        self.buttons_frame.pack(side=tk.TOP)

        # var
        self.oryginal_image = oryginal_image
        self.oryginal_frames = oryginal_with_frames
        self.pixel_cords = pixel_cords
        self.pixel_colors = pixel_colors
        self.available_colors = []
        self.width, self.height = oryginal_image.size
        self.score = 0
        self.colored = []
        self.info_score_var = tk.StringVar()
        self.info_amount_var = tk.StringVar()
        self.is_space_pressed = False

        # assigning numbers for colors
        self.create_numbers_for_pixels()
        self.chosen_color = self.available_colors[0]

        # creating upper informations
        self.info()

        # creating canvas for image
        self.canvas = tk.Canvas(self.canvas_frame, width=IMAGE_CANVAS_WIDTH, height=IMAGE_CANVAS_HEIGHT,
                                scrollregion=(0, 0, self.width, self.height))

        # creating working scrollbar
        self.scroll()

        # white-black image
        ie = ImageEnhance.Color(self.oryginal_frames)
        white_black = ImageTk.PhotoImage(ie.enhance(0.2))
        self.canvas.create_image(0, 0, image=white_black, anchor='nw')

        # writing numbers of boxes on canvas
        self.writing_boxes_by_num()

        # creating buttons
        self.buttons()

        # default binds
        self.root.bind('<space>', self.space_pressed)
        self.root.bind('<Key>', self.key_pressed)
        self.canvas.bind('<Button-1>', self.mouse_clicked)

        # pack canvas and loop
        self.canvas.pack(side=tk.LEFT)
        self.root.mainloop()

    def space_pressed(self, e):
        # turn off coloring mode
        if self.is_space_pressed:
            self.is_space_pressed = False
            self.frame2.configure(bg='lavender')
            self.canvas.unbind('<Motion>')
            self.canvas.bind('<Button-1>', self.mouse_clicked)

        # turn on coloring mode
        else:
            self.is_space_pressed = True
            self.frame2.configure(bg='black')
            self.canvas.unbind('<Button-1>')
            self.canvas.bind('<Motion>', self.mouse_clicked)

    def mouse_clicked(self, e):
        mx = self.canvas.canvasx(e.x)
        my = self.canvas.canvasy(e.y)

        for i in range(len(self.pixel_cords)):
            cord = self.pixel_cords[i]

            x1, y1 = cord[0], cord[1]
            x2, y2 = cord[2], cord[3]

            # searching for pixel under cursor
            if (x1 < mx < x2) and (y1 < my < y2):
                color = self.pixel_colors[i]

                # right choice right color chosen
                if self.chosen_color == color:

                    # is that color already colored
                    if cord not in self.colored:
                        self.score += 1
                        self.info_amount_var.set('{}/{}'.format(self.score, len(self.pixel_cords)))
                        self.colored.append(cord)

                    # RGB TO HEX
                    hex_color = rgb_to_hex(color)
                    self.canvas.create_rectangle(cord, fill=hex_color, outline=hex_color)

                    # #if win ZMIANA
                    if self.score == len(self.pixel_cords):
                        print('CONGRATS THAT WILL BE FINISHED IN THE FUTURE')
                        pass
                        # add window with oryginal image and option with save

                # if wrong choice
                else:

                    # if already colored
                    if cord in self.colored:
                        self.score -= 1
                        self.info_amount_var.set('{}/{}'.format(self.score, len(self.pixel_cords)))
                        self.colored.remove(cord)

                    font = ('Comic Sans MS', 8, 'bold italic')
                    hex_color = 'red'
                    self.canvas.create_rectangle(cord, fill=hex_color, outline=hex_color)

                    # writing number of wrong pixel
                    midx, midy = int((cord[0] + cord[2]) / 2), int((cord[1] + cord[3]) / 2)
                    num = self.available_colors.index(color)
                    if color[0] > 180 and color[1] > 280 and color[2] > 180:
                        self.canvas.create_text(midx, midy, fill='black', text=num+1, font=font)
                    else:
                        self.canvas.create_text(midx, midy, fill='white', text=num+1, font=font)

                break

    def key_pressed(self, e):
        numbers = ('1', '2', '3', '4', '5', '6', '7', '8', '9')
        key = e.char
        if key in numbers:
            if int(key) <= len(self.available_colors):
                self.button_pressed(int(key) - 1)

    def create_numbers_for_pixels(self):
        # list for every avaible color
        for obj in self.pixel_colors:
            if obj not in self.available_colors:
                self.available_colors.append(obj)

        # duplicate last color if colors < buttons
        while len(self.available_colors) < HOW_MANY_COLORS:
            self.available_colors.append(self.available_colors[-1])

    def writing_boxes_by_num(self):
        font = ('Comic Sans MS', 8, 'bold italic')

        for i in range(len(self.pixel_cords)):
            cord = self.pixel_cords[i]
            color = self.pixel_colors[i]

            midx, midy = int((cord[0] + cord[2]) / 2), int((cord[1] + cord[3]) / 2)

            num = self.available_colors.index(color)

            # if bg is light text is black
            if color[0] > 180 and color[1] > 180 and color[2] > 180:
                self.canvas.create_text(midx, midy, fill='black', text=num+1, font=font)
            # if bg is dark text is white
            else:
                self.canvas.create_text(midx, midy, fill='white', text=num+1, font=font)

    def buttons(self):
        font = ('Comic Sans MS', 10, 'bold italic')

        # button 1
        rgb_color = self.available_colors[0]
        hex_color = rgb_to_hex(rgb_color)
        if rgb_color[0] > 180 and rgb_color[1] > 180 and rgb_color[2] > 180:

            button1 = tk.Button(self.buttons_frame, text='1', font=font,
                                bg=hex_color,
                                fg='black', command=lambda: self.button_pressed(0))
        else:
            button1 = tk.Button(self.buttons_frame, text='1', font=font,
                                bg=hex_color,
                                fg='white', command=lambda: self.button_pressed(0))

        button1.grid(row=0, column=0, sticky='NW', ipadx=int(self.width / 9))

        # button 2
        if HOW_MANY_COLORS >= 2:
            rgb_color = self.available_colors[1]
            hex_color = rgb_to_hex(rgb_color)
            if rgb_color[0] > 180 and rgb_color[1] > 180 and rgb_color[2] > 180:

                button2 = tk.Button(self.buttons_frame, text='2', font=font,
                                    bg=hex_color,
                                    fg='black', command=lambda: self.button_pressed(1))
            else:
                button2 = tk.Button(self.buttons_frame, text='2', font=font,
                                    bg=hex_color,
                                    fg='black', command=lambda: self.button_pressed(1))

            button2.grid(row=0, column=1, sticky='NW', ipadx=int(self.width / 9))

        # button 3
        if HOW_MANY_COLORS >= 3:
            rgb_color = self.available_colors[2]
            hex_color = rgb_to_hex(rgb_color)
            if rgb_color[0] > 180 and rgb_color[1] > 180 and rgb_color[2] > 180:

                button3 = tk.Button(self.buttons_frame, text='3', font=font,
                                    bg=hex_color,
                                    fg='black', command=lambda: self.button_pressed(2))
            else:
                button3 = tk.Button(self.buttons_frame, text='3', font=font,
                                    bg=hex_color,
                                    fg='white', command=lambda: self.button_pressed(2))

            button3.grid(row=0, column=2, sticky='NW', ipadx=int(self.width / 9))

        # button 4
        if HOW_MANY_COLORS >= 4:
            rgb_color = self.available_colors[3]
            hex_color = rgb_to_hex(rgb_color)
            if rgb_color[0] > 180 and rgb_color[1] > 180 and rgb_color[2] > 180:

                button4 = tk.Button(self.buttons_frame, text='4', font=font,
                                    bg=hex_color,
                                    fg='black', command=lambda: self.button_pressed(3))
            else:
                button4 = tk.Button(self.buttons_frame, text='4', font=font,
                                    bg=hex_color,
                                    fg='white', command=lambda: self.button_pressed(3))

            button4.grid(row=1, column=0, sticky='NW', ipadx=int(self.width / 9))

        # button 5
        if HOW_MANY_COLORS >= 5:
            rgb_color = self.available_colors[4]
            hex_color = rgb_to_hex(rgb_color)
            if rgb_color[0] > 180 and rgb_color[1] > 180 and rgb_color[2] > 180:

                button5 = tk.Button(self.buttons_frame, text='5', font=font,
                                    bg=hex_color,
                                    fg='black', command=lambda: self.button_pressed(4))
            else:
                button5 = tk.Button(self.buttons_frame, text='5', font=font,
                                    bg=hex_color,
                                    fg='white', command=lambda: self.button_pressed(4))

            button5.grid(row=1, column=1, sticky='NW', ipadx=int(self.width / 9))

        # button 6
        if HOW_MANY_COLORS >= 6:
            rgb_color = self.available_colors[5]
            hex_color = rgb_to_hex(rgb_color)
            if rgb_color[0] > 180 and rgb_color[1] > 180 and rgb_color[2] > 180:

                button6 = tk.Button(self.buttons_frame, text='6', font=font,
                                    bg=hex_color,
                                    fg='black', command=lambda: self.button_pressed(5))
            else:
                button6 = tk.Button(self.buttons_frame, text='6', font=font,
                                    bg=hex_color,
                                    fg='white', command=lambda: self.button_pressed(5))

            button6.grid(row=1, column=2, sticky='NW', ipadx=int(self.width / 9))

        # button 7
        if HOW_MANY_COLORS >= 7:
            rgb_color = self.available_colors[6]
            hex_color = rgb_to_hex(rgb_color)
            if rgb_color[0] > 180 and rgb_color[1] > 180 and rgb_color[2] > 180:

                button7 = tk.Button(self.buttons_frame, text='7', font=font,
                                    bg=hex_color,
                                    fg='black', command=lambda: self.button_pressed(6))
            else:
                button7 = tk.Button(self.buttons_frame, text='7', font=font,
                                    bg=hex_color,
                                    fg='white', command=lambda: self.button_pressed(6))

            button7.grid(row=2, column=0, sticky='NW', ipadx=int(self.width / 9))

        # button 8
        if HOW_MANY_COLORS >= 8:
            rgb_color = self.available_colors[7]
            hex_color = rgb_to_hex(rgb_color)
            if rgb_color[0] > 180 and rgb_color[1] > 180 and rgb_color[2] > 180:

                button8 = tk.Button(self.buttons_frame, text='8', font=font,
                                    bg=hex_color,
                                    fg='black', command=lambda: self.button_pressed(7))
            else:
                button8 = tk.Button(self.buttons_frame, text='8', font=font,
                                    bg=hex_color,
                                    fg='white', command=lambda: self.button_pressed(7))

            button8.grid(row=2, column=1, sticky='NW', ipadx=int(self.width / 9))

        # button 9
        if HOW_MANY_COLORS >= 9:
            rgb_color = self.available_colors[8]
            hex_color = rgb_to_hex(rgb_color)
            if rgb_color[0] > 180 and rgb_color[1] > 180 and rgb_color[2] > 180:

                button9 = tk.Button(self.buttons_frame, text='9', font=font,
                                    bg=hex_color,
                                    fg='black', command=lambda: self.button_pressed(8))
            else:
                button9 = tk.Button(self.buttons_frame, text='9', font=font,
                                    bg=hex_color,
                                    fg='white', command=lambda: self.button_pressed(8))

            button9.grid(row=2, column=2, sticky='NW', ipadx=int(self.width / 9))

    def button_pressed(self, num):
        self.chosen_color = self.available_colors[num]
        self.info_score_var.set(self.available_colors.index(self.chosen_color) + 1)

    def scroll(self):
        scrollx = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        scrollx.pack(side=tk.BOTTOM, fill=tk.X)
        scrollx.config(command=self.canvas.xview)

        scrolly = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        scrolly.config(command=self.canvas.yview)

        self.canvas.config(xscrollcommand=scrollx.set, yscrollcommand=scrolly.set)

    def info(self):
        font = ('Comic Sans MS', 15, 'bold italic')

        # default StringVars
        self.info_score_var.set(self.available_colors.index(self.chosen_color) + 1)
        self.info_amount_var.set('0/{}'.format(len(self.pixel_cords)))

        frame1 = tk.Frame(self.info_frame)
        frame1.grid(row=0, column=0, padx=10)
        self.frame2 = tk.Frame(self.info_frame, bg="lavender", bd=2, relief=tk.RIDGE)
        self.frame2.grid(row=0, column=1, padx=10)
        frame3 = tk.Frame(self.info_frame)
        frame3.grid(row=0, column=2, padx=10)

        label_kolor = tk.Label(frame1, textvariable=self.info_score_var, font=font,
                               fg='black')

        label_spacja = tk.Label(self.frame2, text='Space', font=font, fg='black')

        label_pkt = tk.Label(frame3, textvariable=self.info_amount_var, font=font)

        label_kolor.pack()
        label_spacja.pack()
        label_pkt.pack()


if __name__ == '__main__':

    # info and warnings
    print('\n~~~\nINFORMATIONS and WARNINGS\n'
          '-resolution of image- the higher the resolution, the longer you wait,\n'
          'if you chose to low resolution image will be so blurred\n\n'
          '-pixel size- you can choose pixel size, the bigger it is, the image is less clear,\n'
          'but the smaller it is, the pixels is harder to see and aim, pixel size depends on your comp'
          'and image resolution,\n'
          'cuz size is given in pixels of your screen, so choose your best!\n\n'
          'colors amount- how many colors will have your photo (between 1-9)\n'
          'the bigger it is the more colorful and clearly image is\n\n'
          '-enter names of file with extension! (e.g smutnazaba.jpg), avaible extension: jpg, png\n\n'
          '-store images in dictionary named "{}" placed in the same dictionary as this file!!!\n'
          'if does not exist- just make it\n\n'
          '-do not forget about scrollbars, because sometimes you may be confused, you did not colored everything,'
          '\n when after scrolling you will have additional line\n\n'
          '-you can switch between coloring mode- coloring everything under cursor or coloring only when you right-clic'
          'k\n to switch- press space\n\n'
          '-you can choose a color -by pressing buttons on the screen -or by pressing 1-9 keys on keyboard\n'
          '~~~'.format(IMAGE_DICTIONARY[:-1]))

    # sure u read
    input('If you read it carefully, press enter\n')

    # image name
    image_name = input('Image name (*.png or *.jpg): ')
    if image_name[-4:] != '.jpg' or image_name[-4:] != '.png':
        print('Wrong extension')
        input('Press enter to quit\n')
        sys.exit()
    PATH = IMAGE_DICTIONARY + image_name

    # pixel size
    try:
        PIXEL_SIZE = int(input('Pixel size (recommend around 15-30 depends on resolution): '))
    except:
        print('Wrong pixel size')
        input('Press enter to quit\n')
        sys.exit()

    # colors
    try:
        HOW_MANY_COLORS = int(input('Colors amount (1-9): '))
        if HOW_MANY_COLORS < 1 or HOW_MANY_COLORS > 9:
            print('Wrong colors amount')
            input('Press enter to quit\n')
            sys.exit()
    except:
        print('Wrong colors amount')
        input('Press enter to quit\n')
        sys.exit()

    img = IMG()
    cords = img.pixel_cords
    colors = img.pixel_colors

    GUI(cords, colors)
