# -*- coding: utf-8 -*-
"""
guistil.py   v0.2 (2020-11)
"""

# Copyright 2020-2021 Dominik Zobel.
# All rights reserved.
#
# This file is part of the miniSoilLAB package.
# miniSoilLAB is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# miniSoilLAB is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with miniSoilLAB. If not, see <http://www.gnu.org/licenses/>.


import tkinter
from tkinter import ttk


# -------------------------------------------------------------------------------------------------
class GUIFarben(object):
   def __init__(self):
      self.farbe_fg = '#505050';
      self.farbe_bg = '#eeeeee';
      self.farbe_bg_hover = '#cccccc';
      self.farbe_fg_hover = '#202020';
      self.farbe_bg_highlight = '#505050';
      self.farbe_fg_highlight = '#eeeeee';
      self.farbe_bg_inaktiv = self.farbe_bg;
      self.farbe_fg_inaktiv = '#bbbbbb';
      self.farbe_bg_subitem = '#dddddd';
      self.farbe_bg_subitem_highlight = '#60aacc';
      self.farbe_bg_active = self.farbe_bg_subitem;
      self.farbe_fg_active = '#aa0000';
      self.farbe_fg_scrollbar = '#808080';
#


# -------------------------------------------------------------------------------------------------
class CustomOptionMenu(tkinter.OptionMenu):
   def __init__(self, refelem, *args, **kwargs):
      farben = GUIFarben();
      font = ('Helvetica', '14');#      # Am besten einheitlich in Pixel
      #
      super().__init__(refelem, *args, **kwargs);
      #
      self.configure(background='#ffffff', foreground=farben.farbe_fg_active,
         highlightcolor=farben.farbe_fg_active, activebackground=farben.farbe_bg_active,
         activeforeground=farben.farbe_fg_active, font=font, highlightthickness=0,
         borderwidth=0, indicatoron=0);
      #
      self['menu'].configure(borderwidth=0, activeborderwidth=0, font=font,
         foreground='#404040', background='#ffffff', selectcolor=farben.farbe_fg_active,
         activebackground=farben.farbe_bg_active, activeforeground=farben.farbe_fg_active);
#


# -------------------------------------------------------------------------------------------------
class CustomScrollbar(ttk.Scrollbar):
   def __init__(self, refelem, *args, **kwargs):
      farben = GUIFarben();
      style = ttk.Style();
      style.layout('arrowless.Vertical.TScrollbar',
               [('Vertical.Scrollbar.trough',
               {'children': [('Vertical.Scrollbar.thumb',
                              {'expand': '1', 'sticky': 'nswe'})],
                  'sticky': 'ns'})]);
      #
      style.configure('arrowless.Vertical.TScrollbar', troughcolor=farben.farbe_bg_hover,
         highlightthickness=0, elementborderwidth=0, borderwidth=0, width=16,
         background=farben.farbe_fg_scrollbar);
      style.map('arrowless.Vertical.TScrollbar', background=[('disabled', farben.farbe_bg_hover)]);
      #
      super().__init__(refelem, style='arrowless.Vertical.TScrollbar', *args, **kwargs);
#


# -------------------------------------------------------------------------------------------------
class CustomAuswahlliste(tkinter.Frame):
   def __init__(self, refelem, schluessel, *args, **kwargs):
      farben = GUIFarben();
      styleinformation = {'background':         farben.farbe_bg_highlight,
                          'borderwidth':        0,
                          'padx':               10,
                          'pady':               10,
                          'highlightthickness': 0};
      modkeywords = kwargs;
      for eintrag in styleinformation.keys():
         if (eintrag not in modkeywords):
            modkeywords.update([(eintrag, styleinformation[eintrag])]);
      #
      super().__init__(refelem, *args, modkeywords);
      #
      optionList = tkinter.StringVar();
      optionList.set(schluessel);
      auswahlbox = tkinter.Listbox(self, listvariable=optionList, selectmode='multiple',
         foreground=farben.farbe_bg_highlight, background=farben.farbe_fg_highlight,
         selectbackground=farben.farbe_bg_active, selectforeground=farben.farbe_fg_active,
         font=('Helvetica', '-16'), borderwidth=0, highlightthickness=0, activestyle='none',
         width=30);
      # FIXME: Listbox wird trotz sticky='nsew' nicht horizontal zentriert und skaliert
      auswahlbox.grid(row=0, column=0, sticky='nsew');
      auswahlbox.focus_set();
      #
      scrollbar = CustomScrollbar(self, orient='vertical');
      scrollbar.grid(column=1, row=0, sticky='ns')
      #
      auswahlbox.configure(yscrollcommand=scrollbar.set)
      scrollbar.config(command=auswahlbox.yview)
#


# -------------------------------------------------------------------------------------------------
class CustomEntry(tkinter.Entry):
   def __init__(self, refelem, *args, **kwargs):
      farben = GUIFarben();
      styleinformation = {'background':         '#ffffff',
                          'foreground':         farben.farbe_fg,
                          'borderwidth':        0,
                          'insertborderwidth':  0,
                          'selectborderwidth':  0,
                          'highlightthickness': 0,
                          'font':               ('Helvetica', '-14')};
      modkeywords = kwargs;
      for eintrag in styleinformation.keys():
         if (eintrag not in modkeywords):
            modkeywords.update([(eintrag, styleinformation[eintrag])]);
      #
      super().__init__(refelem, *args, modkeywords);
#


# -------------------------------------------------------------------------------------------------
class CustomLabel(tkinter.Label):
   def __init__(self, refelem, *args, **kwargs):
      farben = GUIFarben();
      styleinformation = {'background': farben.farbe_bg_highlight,
                          'foreground': farben.farbe_fg_highlight,
                          'font':       ('Helvetica', '-16')};
      modkeywords = kwargs;
      for eintrag in styleinformation.keys():
         if (eintrag not in modkeywords):
            modkeywords.update([(eintrag, styleinformation[eintrag])]);
      #
      super().__init__(refelem, *args, modkeywords);
#


# -------------------------------------------------------------------------------------------------
class CustomCheckbutton(tkinter.Label):
   def __init__(self, refelem, variable, *args, **kwargs):
      icon_normal = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAALCAYAAAB24g05AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAACsSURBVCiR3ZIhDkIxEERnKr4k3UOQoDgC4nMbErBchIQjgEcjuAKaA2DabnB80UVgoP3w0Yzc2XliMgQAVW1zzhsAEwBErRuAvYgsSXZvTghhlFK6qurczPrCSCn5GOMhxrguPUdyamYX7/2RpPUBREQBbAHMKoBzrjGze1/wVTnnjmRTAYaCQ/oHwKdyqsdn2V11N7MzybGqtt92AGAB4FR6BH5e4k5EVuUSH//nUEgTNCwAAAAAAElFTkSuQmCC';
      self.image_normal = tkinter.PhotoImage(data=icon_normal);
      icon_checked_hover = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAALCAYAAAB24g05AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGFSURBVCiRdZE9aJNRGIWfc9O0CURc3F2cDDgkXzJ0ECMIgiIOQt1cHKSDwbnFn8EKTmK3Di7SJYUODiIun0LIkpvJxRoHHd1MFCwx+Y5LAx9Nfbd7znneH64AYowtYBs4D4jFGgMPbR9KqiZJcn9uqNvtniqVSl+yLLvdbDY/ngATYzyTZdl6COExINtbjUZjAyCsrKxcAL7+Dz6qdgjhyXw7SZfTNC0BBEnLwPc0TZeOU7YVY3wBbObktFwuX2m1WocAIYRwAHyuVCrver1eeZ7qdDqFwWCwA7Rz8NvJZHKtWq3+ngtLtteBDUkUi8X94XB4czQaZbZfA2s5eE/Sm9XV1T/5LYPtX/OHpKvj8bgD7Etay+mvbO8Ad46fGabT6a6krdzdN4DruczLWq12l5O/l1AoFM7aPgc8O25KepokSVuSJS3bniw0mM1mn4CLtt9Lep7zHtXr9U2AGONp4J6kDwtDAPr9/iVJ25IObP+w/U3SLaB5lPtpe1fSgyRJ/uYb/APaT5Minc9lswAAAABJRU5ErkJggg==';
      self.image_checked_hover = tkinter.PhotoImage(data=icon_checked_hover);
      icon_checked = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAALCAYAAAB24g05AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAF5SURBVCiRdZE9i1NhFISfuTcsShBzbyRdkICVgqWlXyAIilgI/gELsTBYWbisWKyClbidhY0uwgoWFiI26m+wcUGIkkIk5H1DNLiYmx0LjbzsxtOdmfMMA0cAMcZTtteAw4DYPWNJK7a3gCNlWV7/5wwGg30hhK8xxhMLwD/0eHwgxrgSQtgOITiEsDr3sjzPjwKfiqJ4/7+A6XTatX0naXe61+vtAcgkLQFfbNd2grY1HA4fSFpO5LdVVZ3pdDpbAFlVVZuSPoYQXvf7/b0JnI9Go0eSugn8ajKZnGu1Wj/mQi3P82u2b0miXq+/sH0R2I4xPgEuzw8lPbf9st1u/0xb1oDvyX42xrgBZMD5BH4s6RlwE3iaBmS214G7iXYhhW0/bDQaV2az2aL3kkk6CBwC7i3wV5vNZleSJS3Z/rUrwPYH4LikN8D9pPbtsiyXAUII+4GrwLudAQKIMZ60vSZp0/Y34LOkS7aP/b0bAetFUdyQNE0DfgMcA6Sn+wiDxAAAAABJRU5ErkJggg==';
      self.image_checked = tkinter.PhotoImage(data=icon_checked);
      icon_unchecked_hover = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAALCAYAAAB24g05AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGCSURBVCiRdZG/ixNRFIW/+zLZiYURgr2NlYJVmFJUkMkPEQtB/wALsTBYWeyiR9AVLIK4nYWNLkLsJCODjQrp8jobVyy0CjZB1GLRSZ5NIuNuvN2953znXrgG4L0/DWwBxwBjf30HbmVZthtCOC7p+lKw0Wh0sFarfZzP55eTJHm3AsZ7fzjP82tFUWixYFPSOoCL4/gE8Ol/MMBwOOwVRXGndN0ZSTUAZ2ZrwBdJ0QrWJD0ENkqzN8BZSbsAzjm3k+f5ByDv9/sHlq7BYFCR9BjoleBX9Xq9K+lnecNdYH3R541G40Icx/PJZPIUuPTXaPai3W6/TJLkWfnEyMx+hBCWfWs6nQ4AB5wr+Z50Op3nzrmbwD8BLk3T7SiKNkuz83vgR5KusPq9uEqlcqTVah0F7q/Q70nqAcHM1kIIv/YFzGaz98DJbrf7GnhQ0m5L2gDw3h8CrprZ270BBjAej0+Z2VYIYSfLsq/VavVzmqYXgWTh+xZC2DazG81m83c54A+6RYYOt+lCzAAAAABJRU5ErkJggg==';
      self.image_unchecked_hover = tkinter.PhotoImage(data=icon_unchecked_hover);
      #
      self.status = variable;
      #
      self.farben = GUIFarben();
      styleinformation = {'compound':            'left',
                          'image':               self.image_normal,
                          'font':                ('Helvetica', '-16'),
                          'background':          self.farben.farbe_bg_highlight,
                          'foreground':          self.farben.farbe_fg_highlight,
                          'highlightthickness':  0,
                          'borderwidth':         0,
                          'border':              0,
                          'relief':              'flat'};
      modkeywords = kwargs;
      for eintrag in styleinformation.keys():
         if (eintrag not in modkeywords):
            modkeywords.update([(eintrag, styleinformation[eintrag])]);
      #
      super().__init__(refelem, *args, modkeywords);
      #
      self.bind('<Enter>', self.MouseOver);
      self.bind('<Leave>', self.MouseOut);
      self.bind('<Button-1>', self.CheckUncheck);
   #
   def MouseOver(self, event):
      if (self.status.get() == 0):
         hoverimage = self.image_unchecked_hover;
      else:
         hoverimage = self.image_checked_hover;
      #
      event.widget.configure(foreground=self.farben.farbe_bg_hover, image=hoverimage);
   #
   def MouseOut(self, event):
      if (self.status.get() == 0):
         grundbild = self.image_normal;
      else:
         grundbild = self.image_checked;
      #
      event.widget.configure(foreground=self.farben.farbe_fg_highlight, image=grundbild);
   #
   def CheckUncheck(self, event):
      if (self.status.get() == 0):
         self.status.set(1);
      else:
         self.status.set(0);
      #
      self.MouseOver(event);
#


# -------------------------------------------------------------------------------------------------
class CustomButton(tkinter.Button):
   def __init__(self, refelem, *args, **kwargs):
      farben = GUIFarben();
      styleinformation = {'background':          farben.farbe_bg,
                          'foreground':          farben.farbe_fg,
                          'highlightbackground': farben.farbe_bg_hover,
                          'activebackground':    farben.farbe_bg_hover,
                          'activeforeground':    farben.farbe_fg_active,
                          'font':                ('Helvetica', '-16'),
                          'highlightthickness':  0,
                          'borderwidth':         0,
                          'border':              0,
                          'relief':              'flat',
                          'overrelief':          'flat'};
      modkeywords = kwargs;
      for eintrag in styleinformation.keys():
         if (eintrag not in modkeywords):
            modkeywords.update([(eintrag, styleinformation[eintrag])]);
      #
      super().__init__(refelem, *args, modkeywords);
#


# -------------------------------------------------------------------------------------------------
class CustomRadioItem(ttk.Frame):
   def __init__(self, *args, **kwargs):
      self.font = ('Helvetica', '-16');
      self.font_klein = ('Helvetica', '-14');
      self.font_klein_italics = ('Helvetica', '-14', 'italic');
      #
      icon_hover = b'iVBORw0KGgoAAAANSUhEUgAAACQAAAAMCAYAAAAK/x/DAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFWSURBVDiNtZU7TsNAEIb/WSwTWRZJ4YoYeaOkWzoepwBxgFCDlA5SEYkjBOpA7RPACSixEAUkfZDp4yIvZ6OhIBIQxTJFdsqZb7VfMfsvwVAppezRaHTGzHUAatF+Z+bQdd37brebrjpHJmR83y9blvXIzDGA20KhEAHAZDI5EEJcMvO21vo4juNPE/f/qVqttimlfA2CoJXFVCqVaynli1LKXp5trFuoWCw2AHj9fr+RxQwGg6dSqXSSpulWkiTR75lYt9BiZ27+wbWJ6HS5b0JIjcfjKI9zXfcZP8tuTggAPM/LfSzT6VQAYONCRNQbDof7edxsNtsD0DMuBCAEcJEHCSGaRBQaF7IsqwNASimvspggCFrMXHYc5255ZiQYq9Xqznw+fwDwAaCdpmkEALZtHzJzk4h8rfXRqmA0IgR8B6TW+hxAHcDuov1GRKHjOJ2sr+MLZ295zxSVTOUAAAAASUVORK5CYII=';
      self.image_hover = tkinter.PhotoImage(data=icon_hover);
      icon_highlight = b'iVBORw0KGgoAAAANSUhEUgAAACQAAAAMCAYAAAAK/x/DAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAEUSURBVDiNvZQxTsNAEEX/X2IoVhGVC8AUid1Z4g5wFBrMVTgASjgMHAK5QhYUSURnhLUNGu/QpDIbQUQ2U868kZ5mNENEirIsD51zFYAKwHSdbrz3s/F4PK/r+ivUxxgyWZadJUny5L0/JWkHZQdgKSJXi8ViGV2oKIqjvu+fvfcTkqMQQ1JUtbHWXgwnZXYtJCLVejJBGQBQ1RGArOu6m2Ft50IAqsCaQmGNMbf7EJr+jmxmYwjpf9gYQm9bsK/DxM6FjDFzVXV/QB2A2T6E7gG8q2q/iVFVAbCy1v4QivIY8zw/F5FHACfDi1NVR3IlIpehx3gQQ6ht2880TR9UtQMwIXlM0gN4IXlnrb1umuYj1PsN8glsPeU76hoAAAAASUVORK5CYII=';
      self.image_highlight = tkinter.PhotoImage(data=icon_highlight);
      icon_inaktiv = b'iVBORw0KGgoAAAANSUhEUgAAACQAAAAMCAYAAAAK/x/DAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFMSURBVDiNvZW/S4JhEICf95XvVXDRNQvaa+sHNCtOBU0utlZzNRU0BW3WXM0uNhYfKJ975Fj0B/QD2l4XEUXuWoxAlG/x68a75+DhOO4MCUWj0XD5fP4AqAIr4/Srqta73e5dpVIZTuszSci02+2CiDwCnyJync1mOwC9Xm/DWnsMLFhrd4rF4lfiQmEYpoMgeFLV+3K5fDmNiaLoXFV3vfdbk5Oy8xYKguDAGPMxSwagVCpdAN+5XG5/sjZ3IaCqqldxkIjUjDF7/yG0IiKdOMg598zfsicqhHMudjf7/b4FNHEhVX0bjUbrcZxzbg14S1zIWlsHjuI4VT0B6okLDYfDG2A5iqLTWUyr1ToDCt7728laIoex2WwupVKpB+BdRGqDwaADkMlkNoETYNFau/0vh/E3wjBMO+cORaRqjFkdp1+Auvf+Ztbr+AH4yHwUoBygvgAAAABJRU5ErkJggg==';
      self.image_inaktiv = tkinter.PhotoImage(data=icon_inaktiv);
      icon_normal = b'iVBORw0KGgoAAAANSUhEUgAAACQAAAAMCAYAAAAK/x/DAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFESURBVDiNvZW9SgNBFIXPyc446dIbBfvY+QM+wsLKTpMqtsZaUylYCXbROlpvtU2C+xBiSiUP4A/4AGFZ3MmOTQISEtYik1ve+w18DJdzCUfVbDY38jxvW2tbJBvT9hvJSAjxGMfxz6J3dCETBEFdCJEA+CR5P5lMhgDged5BURQXJDeNMcdJknw5F/J9Xymlnq218WAwuF3EaK2vAWgp5dH8T1VWLaSUagP4WCYDAP1+/wbAtzHmdH62ciEALQB3ZRDJblEUJ+sQaqRpOiyDhBAvf5bdqRBqtVrpbo7H4woAuw6hUZ7n+2WQlHLPWjtyLkQyInn+D65DMnIulGVZD8CO1vpyGROG4RXJupTyYX7mJBjDMNwm+QTgnWTXGDMLxkMAHQBbxphgLcE4K9/3VbVaPbPWtgDsTtuvACIpZW/Z6fgF4k5tF6eUZz8AAAAASUVORK5CYII=';
      self.image_normal = tkinter.PhotoImage(data=icon_normal);
      icon_leer = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAABCAYAAADeko4lAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAMSURBVAiZY2CgMgAAAFEAAQeRRhEAAAAASUVORK5CYII=';
      self.image_leer = tkinter.PhotoImage(data=icon_leer);
      icon_command = b'iVBORw0KGgoAAAANSUhEUgAAACQAAAAMCAYAAAAK/x/DAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAEISURBVDiNvZKhTsRAEIb/nSWpvwdA0lJXwyPgmnbFShJOIzHIPgUGTmFIKgYEJNQisBWIbjAYkCS1bcqiLmku3WL2+skvmcyXyUh4Rin1HobhpzHmY865IN9BwzCcA9hkWbaecy6k7yBjzHccx88AbqMokk3TvE0517zwHbQlTdNDKWUlhHhg5iuXWywIALTWq67rngDUSZJcFEXxO+XGM95/aExZlj/W2lMhxFFd13cut1gQAARBYAEM1lqac4sEaa1Xfd9XAL7atj1zuTF7fWoieiGix/FT77pd9nIhpdSxlPKViG62i6fcFN4vlOf5CQAWQlwy873LuTjwHQTgGsCamat/3CR/YouZ7YqdqyMAAAAASUVORK5CYII=';
      self.image_command = tkinter.PhotoImage(data=icon_command);
      icon_command_hover = b'iVBORw0KGgoAAAANSUhEUgAAACQAAAAMCAYAAAAK/x/DAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAD4SURBVDiNvZIxTsMwGEa/EEsZ/8izVX/2gMQFOELP0JWZjVNwCDYWLgDsSBVS1aEDAxIDrhQYm3gnwFKkUCXpkuSNT7K+J9spBobki4iEGONbn+siHTpIa70CcJfn+a6qqk2XmyyoLMtPEXlIkuRGRNIY43ObG3r3KN77GclXktd97pBkzChjjFZK3QPYhBAuAXy3ueaZkzGDiqLYZVk2B3BK8rbLTRYEAEqpHwB1c6vN/TH4p25ijNF1XT8CeA8hXGD/ZIeueWa0G/Lez5RSSwBP++GvNjfW/j+stWckt9baqz43Cc65c5IfJBd9bsqgtXNufsx18QuJ8HZocuQR8gAAAABJRU5ErkJggg==';
      self.image_command_hover = tkinter.PhotoImage(data=icon_command_hover);
      #
      super().__init__(*args, **kwargs);
      self.farben = self.master.farben;
      self.breite = self.master.breite;
      self.subframe = ttk.Frame(self);
   #
   def MouseOver(self, event):
      event.widget.configure(foreground=self.farben.farbe_fg_hover, background=self.farben.farbe_bg_hover,
         image=self.image_hover);
   #
   def MouseOut(self, event):
      event.widget.configure(foreground=self.farben.farbe_fg, background=self.farben.farbe_bg_subitem,
         image=self.image_normal);
   #
   def MouseOverLeer(self, event):
      event.widget.configure(foreground=self.farben.farbe_fg_hover, background=self.farben.farbe_bg_hover,
      image=self.image_command_hover);
   #
   def MouseOutLeer(self, event):
      event.widget.configure(foreground=self.farben.farbe_fg, background=self.farben.farbe_bg_subitem,
      image=self.image_command);
   #
   def Unhighlight(self):
      self.master.currenthighlight.bind('<Enter>', self.MouseOver);
      self.master.currenthighlight.bind('<Leave>', self.MouseOut);
      self.master.currenthighlight.configure(foreground=self.farben.farbe_fg, background=self.farben.farbe_bg_subitem,
         image=self.image_normal);
   #
   def Highlight(self, event, command):
      if (event.widget['background'].string != self.farben.farbe_bg_subitem_highlight):
         event.widget.unbind('<Enter>');
         event.widget.unbind('<Leave>');
         event.widget.configure(foreground=self.farben.farbe_fg_highlight,
            background=self.farben.farbe_bg_subitem_highlight, image=self.image_highlight);
         command();
         #
         if (self.master.currenthighlight is not None):
            self.Unhighlight();
         #
         self.master.currenthighlight = event.widget;
   #
   def NeuerEintrag(self, text, command=None, variable=None):
      if ((command is not None) and (variable is not None)):
         print('# Warnung: Eintrag mit command und variable nicht unterstützt');
         return;
      #
      numeintraege = len(self.subframe.children);
      if (numeintraege == 0):
         self.master.EintragVerlinken(self);
      #
      if (command is not None):
         sublabel = ttk.Label(self.subframe, compound='left', image=self.image_normal, text=text,
            font=self.font, foreground=self.farben.farbe_fg, background=self.farben.farbe_bg_subitem, width=self.breite);
         sublabel.grid(row=numeintraege, column=0, ipady=2, sticky='ew');
         sublabel.bind('<Enter>', self.MouseOver);
         sublabel.bind('<Leave>', self.MouseOut);
         sublabel.bind('<Button-1>', lambda event: self.Highlight(event, command));
      elif (variable is not None):
         subsubframe = tkinter.Frame(self.subframe, background=self.farben.farbe_bg_subitem);
         subsubframe.grid(row=numeintraege, column=0, ipady=2, sticky='nsew');
         sublabel = ttk.Label(subsubframe, compound='left', image=self.image_leer, text=text,
            font=self.font_klein, foreground=self.farben.farbe_fg, background=self.farben.farbe_bg_subitem);
         sublabel.grid(row=0, column=0, sticky='ew');
         subentry = CustomEntry(subsubframe, textvariable=variable, width=5);
         subentry.grid(row=0, column=1, padx=5, sticky='nsew');
      else:
         sublabel = ttk.Label(self.subframe, compound='left', image=self.image_leer, text=text,
            font=self.font_klein_italics, foreground=self.farben.farbe_fg, background=self.farben.farbe_bg_subitem, width=self.breite);
         sublabel.grid(row=numeintraege, column=0, ipady=2, sticky='ew');
   #
   def NeuerFrameEintrag(self):
      refframe = tkinter.Frame(self.subframe, background=self.farben.farbe_bg_subitem);
      refframe.grid(row=len(self.subframe.children)-1, column=0, ipady=2, sticky='nsew');
      return refframe;
   #
   def NeuerBefehl(self, text, command):
      sublabel = ttk.Label(self.subframe, compound='left', image=self.image_command, text=text,
         font=self.font, foreground=self.farben.farbe_fg, background=self.farben.farbe_bg_subitem, width=self.breite);
      sublabel.grid(row=len(self.subframe.children)-1, column=0, ipady=2, sticky='ew');
      sublabel.bind('<Enter>', self.MouseOverLeer);
      sublabel.bind('<Leave>', self.MouseOutLeer);
      sublabel.bind('<Button-1>', lambda event: command());
   #
   def AlleEintraegeEntfernen(self):
      for kindelem in self.subframe.winfo_children():
         kindelem.destroy();
      #
      self.subframe.grid_remove();
      self.master.EintragEntlinken(self);
#


# -------------------------------------------------------------------------------------------------
class CustomLabelMenu(ttk.Frame):
   def __init__(self, farben, breite, hoehe, *args, **kwargs):
      self.font = ('Helvetica', '-20', 'bold');
      #
      icon_highlight = b'iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAACASURBVBiVfdAxDgFRFIXhOyQkFqLRqy1CYg86m9DqLEVhEaKg1VmAGdOI+DSTmLw872/vyTnnnogOXLDBIErggDeumJWESzzwQY0dxjnhBE8/Wtyx+Bef0mCfFh9mWlUR8Uqj255TjRvmaeyq90yDLUa5fsdunhOmpXnOWKPK3b/p6K02D06m2AAAAABJRU5ErkJggg==';
      self.image_highlight = tkinter.PhotoImage(data=icon_highlight);
      icon_hover = b'iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAADeSURBVBiVbZAxS8NQFIXP8ZkIfUsSQocI4Y5Cf4lD94Lg4t4/4ir4A/ofnDtnEnRyeC841pIIlkLFcDuYlGfwmw6XwzmHa9AjIq9Zll20bVsBUIw4C/R713X3IvJSluVsbDSDSNP0AOAawCXJ2yRJpnmer5um6QCAg7EoikkURRuStj/tVfWT5E1d12uG8SLy1KeeUNUdyVW48c+UAZIE8D2u/iA56U9fALYkF9776pQYx/Gc5M9vm+4APFhrr7z3FQCcBy13qmpJPhtjFs65t3BCaJwaY5bOuUf88/Ajk3ZCjr1yFA4AAAAASUVORK5CYII=';
      self.image_hover = tkinter.PhotoImage(data=icon_hover);
      icon_inaktiv = b'iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAADrSURBVBiVfZCxSsRQEEXvvGfYZMXWH0ij+AlpFh4ELOy3SSVY+iMWNsJ2Nn5C4DXvEdItpBK0srCw1SLgSkBkrs0awi54q2E4nLmMxTYxxueqqmZ5nndt2xI7MZP5DcBNURRPTdOc/Qfek/wCcKqq6xDCrfd+tgcOw+CNMRaAkDwCcJUkyWsIYQEAMtXHGD3J8+lORDYkH6anQdLudiMpIvI9Guu6nqdp+g5gvjV9quqHtXbpnOtGY5ZlFwB+AFBENqp61/f9iXOuA4CDP1BVLwEcGmMeASzLsnyZVhhBY8wxgGvn3EpE9h7+CyN2Vj/5eiVdAAAAAElFTkSuQmCC';
      self.image_inaktiv = tkinter.PhotoImage(data=icon_inaktiv);
      icon_normal = b'iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAADhSURBVBiVXY6hTsRAGIRntjRNjmDPoKq2yb0E9sQmW3c1GBIkL4Il4QF4gG7N6eqakoAiDQILDgwEOpi9ptdRk8mX7/8TxJRl+Wytzaqq6tq2FRYxhyLpjeRt3/dPzrnNEkwOxVr7TXJL8twYc1kUxTrP83YYhr8j4ziOe0kJAAI4A3CdZdmr9/4CcZzivd8D2C6ufgF4MPOFZLKAIIkAfiajc25ljHknuYrTJ4APALsQQjcZjTGO5C8AxXN3aZoWIYQOAE5m4JWkUwCPJHd1Xb/MX5hASWtJN03T3EfrUf4Byq9IDI9y9xUAAAAASUVORK5CYII=';
      self.image_normal = tkinter.PhotoImage(data=icon_normal);
      #
      self.farben = farben;
      self.breite = breite;
      self.hoehe = hoehe;
      self.currenthighlight = None;
      #
      super().__init__(*args, **kwargs);
   #
   def MouseOver(self, event):
      event.widget.configure(foreground=self.farben.farbe_fg_hover, background=self.farben.farbe_bg_hover,
         image=self.image_hover);
   #
   def MouseOut(self, event):
      event.widget.configure(foreground=self.farben.farbe_fg, background=self.farben.farbe_bg,
         image=self.image_normal);
   #
   def Highlight(self, event):
      subframe = event.widget.master.children['!frame'];
      if (event.widget['background'].string == self.farben.farbe_bg_highlight):
         event.widget.bind('<Enter>', self.MouseOver);
         event.widget.bind('<Leave>', self.MouseOut);
         subframe.grid_remove();
         self.MouseOver(event);
      else:
         event.widget.unbind('<Enter>');
         event.widget.unbind('<Leave>');
         event.widget.configure(foreground=self.farben.farbe_fg_highlight,
            background=self.farben.farbe_bg_highlight, image=self.image_highlight);
         subframe.grid(row=1, column=0, sticky='nsew');
   #
   def EintragVerlinken(self, element):
      # FIXME: Kann man das immer so sagen?
      baselabel = element.children['!label'];
      baselabel.configure(image=self.image_normal, foreground=self.farben.farbe_fg, background=self.farben.farbe_bg);
      baselabel.bind('<Enter>', self.MouseOver);
      baselabel.bind('<Leave>', self.MouseOut);
      baselabel.bind('<Button-1>', self.Highlight);
   #
   def EintragEntlinken(self, element):
      baselabel = element.children['!label'];
      baselabel.configure(image=self.image_inaktiv, foreground=self.farben.farbe_fg_inaktiv,
         background=self.farben.farbe_bg_inaktiv);
      baselabel.unbind('<Enter>');
      baselabel.unbind('<Leave>');
      baselabel.unbind('<Button-1>');
      self.currenthighlight = None;
   #
   def NeuerEintrag(self, text):
      hauptelement = CustomRadioItem(self);
      hauptelement.grid(row=len(self.children)-1, column=0, sticky='ew');
      labeloption = ttk.Label(hauptelement, compound='left', image=self.image_inaktiv, text=text,
         font=self.font, foreground=self.farben.farbe_fg_inaktiv, background=self.farben.farbe_bg_inaktiv,
         width=self.breite);
      labeloption.grid(row=0, column=0, ipadx=10, ipady=2, sticky='ew');
      return hauptelement;
#

