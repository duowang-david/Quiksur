import tkinter as tk
from tkinter import messagebox
import textwrap
import json
from tkinter import filedialog
import csv

# Create root canvas
root = tk.Tk()
root.title('Quiksur')
# root.iconbitmap('logo.icns')
root.resizable(0, 0)    # disable window resizability


# define main menu class, a subclass of tk.LabelFrame, on left side of the window
class main_menu(tk.LabelFrame):
    def __init__(self, original):
        tk.LabelFrame.__init__(self, original, text='Menu', labelanchor='n', relief='ridge', borderwidth=2, padx=5,
                               pady=5)
        self.grid(row=0, column=0, padx=10, pady=10, sticky='n')
        # Create main menu buttons
        self.button_load_survey = tk.Button(self, text='Load Survey', height=1, width=10, padx=10, pady=10,
                                            command=self.load_survey)
        self.button_export_survey = tk.Button(self, text='Export Survey', height=1, width=10, padx=10,
                                              pady=10, command=self.export_survey)
        self.button_start_survey = tk.Button(self, text='Start Survey', height=1, width=10, padx=10, pady=10,
                                             command=self.start_survey)
        self.button_show_result = tk.Button(self, text='Show Result', height=1, width=10, padx=10,
                                            pady=10, command=self.show_result)
        self.button_export_result = tk.Button(self, text='Export Result', height=1, width=10, padx=10,
                                              pady=10, command=self.export_result)
        self.button_exit = tk.Button(self, text='Exit', height=1, width=10, padx=10, pady=10,
                                     command=original.quit)
        # Display main menu buttons in order
        self.button_load_survey.grid(row=1, column=0, padx=5, pady=5)
        self.button_export_survey.grid(row=2, column=0, pady=5)
        self.button_start_survey.grid(row=3, column=0, pady=5)
        self.button_show_result.grid(row=4, column=0, pady=5)
        self.button_export_result.grid(row=5, column=0, pady=5)
        self.button_exit.grid(row=6, column=0, pady=5)
        # Create frame widget and place it at the lower left corner
        empty_frame = tk.Frame(original, height=125, width=100)
        empty_frame.grid(row=1, column=0)
        empty_frame.propagate()

    # define methods for main menu buttons
    @staticmethod
    def load_survey():
        # load survey from json file /Users
        load_filename = filedialog.askopenfile(initialdir='/Users',
                                               title='Select a file', filetypes=(('json files', '*.json'),
                                                                                 ('all files', '*.*')))
        if load_filename is not None:
            with open(load_filename.name, 'r') as in_file:
                in_data = json.load(in_file)
                for data in in_data:
                    survey_question.append(in_data[data])
        page_control.update_page_status()

    @staticmethod
    def export_survey():
        if len(survey_question) == 0:
            messagebox.showinfo('Alert', 'Your survey is empty!')
        else:
            # export survey to json file
            export_filename = filedialog.asksaveasfile(initialdir='/Users',
                                                       title='Select a directory', filetypes=(('json files', '*.json'),
                                                                                              ('all files', '*.*')))
            if export_filename is not None:
                with open(export_filename.name, 'w') as outfile:
                    out_data = dict()
                    for index, question in enumerate(survey_question):
                        out_data[f'Q{index + 1}'] = question
                    json.dump(out_data, outfile)

    @staticmethod
    def start_survey():
        if len(survey_question) == 0:
            messagebox.showinfo('Alert', 'Your survey is empty!')
        else:
            unedited = 0
            for question in survey_question:
                if not question['is_edited']:
                    unedited += 1
            if unedited != 0:
                messagebox.showinfo('Alert', f'You have {unedited} unedited question!')
            else:
                responder(root)

    @staticmethod
    def show_result():
        if len(answer_record) == 0:
            messagebox.showinfo('Alert', 'No result available!')
        else:
            show_win = tk.Toplevel()
            show_win.transient(root)
            show_win.geometry("260x210")
            show_win.lift()
            show_win.title('Current Result')
            # get control force focus on new window
            show_win.grab_set()
            # set new window position
            x = root.winfo_x()
            y = root.winfo_y()
            show_win.geometry("+%d+%d" % (x + 250, y + 100))
            for index, record in enumerate(answer_record):
                tk.Label(show_win, text='Record ' + str(index+1) + ': ' + '[ID ' + record['ID'] + ']').grid(sticky='w')

    @staticmethod
    def export_result():
        # export result to csv file
        # sample data: [{'ID': '123', '1': ['tdf'], '2': ['sdf'], '3': [3, 'sadf'], '4': [[0, 0, 0, 1, 1, 1], 'dsff']}]
        if len(answer_record) > 0:
            fieldnames = [key for key in answer_record[0]]
            for record in answer_record:
                for item in record:
                    if len(record[item]) == 1:
                        record[item] = str(record[item][0])
                    elif len(record[item]) == 2 and item != 'ID':
                        if type(record[item][0]) == list:
                            results = []
                            for index, result in enumerate(record[item][0]):
                                if result == 1:
                                    results.append(str(index + 1))
                            record[item][0] = ",".join(results)
                            print(record[item][0])
                            record[item] = ",".join([str(record[item][0]), str(record[item][1])])
                        else:
                            record[item] = ",".join([str(record[item][0]), str(record[item][1])])
            export_filename = filedialog.asksaveasfile(initialdir='/Users',
                                                       title='Select a directory', filetypes=(('csv files', '*.csv'),
                                                                                              ('all files', '*.*')))
            if export_filename is not None:
                with open(export_filename.name, 'w') as out_file:
                    w = csv.DictWriter(out_file, fieldnames)
                    w.writeheader()
                    for record in answer_record:
                        w.writerow(record)
                answer_record.clear()
        else:
            messagebox.showinfo('Alert', 'No exportable answer record!')


# define page controller class
class page_controller:
    page_num = 1
    current_page = 1

    def __init__(self):
        # create page status label
        lbl = tk.Label(root, text=f'Page {self.current_page} of {self.page_num}')
        lbl.grid(row=1, column=2, sticky='s', pady=5)
        # create page buttons
        forward = tk.Button(root, text='>>', command=self.page_forward, state=tk.DISABLED)
        backward = tk.Button(root, text='<<', command=self.page_backward, state=tk.DISABLED)
        forward.grid(row=1, column=3, sticky='s' + 'w', pady=5)
        backward.grid(row=1, column=1, sticky='s' + 'e', pady=5)

    @classmethod
    def update_page_status(cls):
        # calculate the number of pages based on the current number of questions
        cls.page_num = len(survey_question) // 10 + 1
        # update page status label
        lbl = tk.Label(root, text=f'Page {cls.current_page} of {cls.page_num}')
        lbl.grid(row=1, column=2, sticky='s', pady=5)
        # if current page is not the last page, set forward button Disable
        if cls.current_page != cls.page_num:
            forward = tk.Button(root, text='>>', command=cls.page_forward, state=tk.NORMAL)
        else:  # if current page is the last page, set forward button Enable
            forward = tk.Button(root, text='>>', command=cls.page_forward, state=tk.DISABLED)
        # if current page is not the first page, set backward button Enable
        if cls.current_page != 1:
            backward = tk.Button(root, text='<<', command=cls.page_backward, state=tk.NORMAL)
        else:  # if current page is the first page, set forward button Disable
            backward = tk.Button(root, text='<<', command=cls.page_backward, state=tk.DISABLED)
        # display buttons onto screen
        forward.grid(row=1, column=3, sticky='s' + 'w', pady=5)
        backward.grid(row=1, column=1, sticky='s' + 'e', pady=5)
        # call update_oncreen_cell method to update questions showed on screen based on updated page number
        cell_control.update_onscreen_cell(cls.current_page, cls.page_num)
        # call update_add_button method to update add_question_button on screen based on updated page number
        cell_control.update_add_button(cls.current_page, cls.page_num)

    @classmethod
    def page_forward(cls):
        # current adds 1
        cls.current_page += 1
        # after changing page, update page status
        cls.update_page_status()

    @classmethod
    def page_backward(cls):
        # current page minus 1
        cls.current_page -= 1
        # after changing page, update page status
        cls.update_page_status()


# define cell controller class, a subclass of tk.LabelFrame, on right side of the window
class cell_controller(tk.LabelFrame):
    onscreen_question_cell = []

    def __init__(self, original):
        # create a labelframe to specify the boundary of of Survey Builder
        tk.LabelFrame.__init__(self, original, text='Survey Builder', labelanchor='n', relief='ridge', borderwidth=2,
                               padx=5, pady=5, height=422, width=520)
        self.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky='n', columnspan=3)
        self.grid_propagate(0)
        # create add_new_question button
        self.add_question_button = tk.Button(self, text='Add New Question', height=1, width=52,
                                             command=self.add_new_cell)
        self.add_question_button.grid(row=13, column=0, columnspan=3, padx=10)

    @classmethod
    def update_onscreen_cell(cls, current, last):
        # first, call destroy method on each question cell to destroy everything in onscreen_question_cell list
        for cell in cls.onscreen_question_cell:
            cell.destroy_cell()
        # if current page is not last page, select 10 questions' index associated with current page and save to a list
        if current != last:
            show_list = [n for n in range(((current - 1) * 10), (current * 10))]
        else:  # if current page is last page, select remained questions' index on last page and save to list
            show_list = [n for n in range(((current - 1) * 10), len(survey_question))]
        # update question cell instances that are to be displayed on screen according to show_list
        for index, ques_id in enumerate(show_list):
            cls.onscreen_question_cell.append(question_cell(index, ques_id))

    # update add_question_button status
    def update_add_button(self, current, last):
        # once current page is not last page, hide add_new_question button
        if current != last:
            self.add_question_button.grid_forget()
        else:  # otherwise, display add_new_question button
            self.add_question_button.grid(row=13, column=0, columnspan=3, padx=10)

    @classmethod
    def add_new_cell(cls):
        # once add_new_question button is pressed, add 'Press to Edit button to edit question' to question data set
        survey_question.append(new_question.copy())
        # then update page status based on updated data set
        page_control.update_page_status()


# define question cell class
class question_cell:

    def __init__(self, cell_id, ques_id):
        self.cell_id = cell_id
        self.ques_id = ques_id
        self.ques_text = survey_question[ques_id]['question_text']
        self.edited = survey_question[ques_id]['is_edited']
        # create question cell frame and question content label
        self.frame = tk.LabelFrame(cell_control, borderwidth=2, padx=5, height=28, width=340, labelanchor='n')
        self.question = tk.Label(self.frame, text=self.ques_text)
        self.frame.grid(row=cell_id, column=1, padx=5, sticky='w')
        self.frame.grid_propagate(0)
        self.question.grid()
        # create question title label
        # check if current question is edited
        if self.edited:  # set question title label background to color #ebfaf7
            self.label = tk.LabelFrame(cell_control, borderwidth=2, padx=5, height=28, width=100, bg='#ebfaf7')
            self.title = tk.Label(self.label, text=f'Question {ques_id + 1}', bg='#ebfaf7')
        else:  # set question title label background to color #fff3e3
            self.label = tk.LabelFrame(cell_control, borderwidth=2, padx=5, height=28, width=100, bg='#fff3e3')
            self.title = tk.Label(self.label, text=f'Question {ques_id + 1}', bg='#fff3e3')
        # display question title label
        self.label.grid(row=cell_id, column=0, padx=5)
        self.label.grid_propagate(0)
        self.title.grid()
        # create edit button
        self.edit = tk.Button(cell_control, text='Edit', padx=5, pady=5, height=1, width=3,
                              command=lambda: question_maker(root, self.cell_id, self.ques_id))
        self.edit.grid(row=cell_id, column=2, padx=5, pady=5)

    # remove all components within question cell instance
    def destroy_cell(self):
        self.label.destroy()
        self.title.destroy()
        self.frame.destroy()
        self.question.destroy()
        self.edit.destroy()


# define question maker class, a subclass of tk.Toplevel, a popup window
class question_maker(tk.Toplevel):

    def __init__(self, original, cell_id, ques_id):
        self.original_frame = original
        tk.Toplevel.__init__(self)
        self.transient(root)
        # self.geometry("660x410")
        self.lift()
        self.title('Question Maker')
        # get control force focus on new window
        self.grab_set()
        # set new window position
        x = root.winfo_x()
        y = root.winfo_y()
        self.geometry("+%d+%d" % (x + 8, y + 30))
        # get cell_id and ques_id
        self.cell_id = cell_id
        self.ques_id = ques_id
        self.ques_text = survey_question[ques_id]['question_text']

        # create button components of lower edit window
        save_button = tk.Button(self, text="Save", command=lambda: self.save_setting())
        save_button.grid(row=2, column=1, sticky='n', padx=5, pady=5)
        delete_button = tk.Button(self, text="Delete", command=lambda: self.delete_ques())
        delete_button.grid(row=2, column=2, sticky='n', padx=5, pady=5)
        cancel_button = tk.Button(self, text="Cancel", command=lambda: self.close_window())
        cancel_button.grid(row=2, column=3, sticky='n', padx=5, pady=5)

        # create question title components within upper frame
        frame = tk.LabelFrame(self, text=f'Question {self.ques_id + 1}', labelanchor='n', relief='ridge', borderwidth=2,
                              padx=5, pady=5, height=350, width=660)
        frame.grid(row=0, column=1, rowspan=2, padx=10, pady=5, sticky='n', columnspan=3)
        frame.grid_propagate(0)
        # separate the upper frame into left and right two invisible frames to sort option entries and drop down menu
        self.left_frame = tk.Frame(frame, height=325, width=540, )
        self.left_frame.grid(row=0, column=0, sticky='n')
        self.left_frame.grid_propagate(0)
        self.right_frame = tk.Frame(frame)
        self.right_frame.grid(row=0, column=1, sticky='n')
        # set title label and question entry to left frame
        title_label = tk.Label(self.left_frame, text='Title', width=9)
        title_label.grid(row=0, column=0)
        self.question_entry = tk.Entry(self.left_frame, width=45)
        self.question_entry.grid(row=0, column=1)
        self.question_entry.insert(0, self.ques_text)
        # create an instance of option manager class, and pass self.left_frame as reference of root to option manager
        self.option_control = option_controller(self.left_frame)
        # set drop down option menu for question types and check boxes to right frame
        # text label for text 'type'
        type_label = tk.Label(self.right_frame, text='Type')
        type_label.grid(row=0, column=0, sticky='w')
        # set up a tkinter variable to store current value of the drop down box
        self.option_value = tk.StringVar(self.right_frame)
        # create and display check boxes below drop down menu on right frame
        self.is_checked = tk.IntVar()
        self.checker_text = ''
        self.checker = tk.Checkbutton()
        # create an input box for notes and explanations
        self.notes_label = tk.Label(self.right_frame, text='Note:')
        self.notes_label.grid(row=2, column=0, pady=5, sticky='w')
        self.notes_input = tk.Entry(self.right_frame, width=9)
        self.notes_input.grid(row=3, column=0, padx=5, columnspan=2, sticky='w')
        # load question note from survey data; load '' for new question
        self.notes_input.insert(0, survey_question[ques_id]['note'])
        # create an instance of option manager class, and pass self.left_frame as reference of root to option manager
        self.option_control = option_controller(self.left_frame)
        # create variable ques_type to store last choice of question type, set default value to 'CO'
        self.ques_type = self.option_value
        # create drop down menu and connect to update_ques_type method
        self.option = tk.OptionMenu(self.right_frame, self.option_value, 'CO', 'YN', 'CH', 'MC', 'LI',
                                    command=self.update_ques_type)
        self.option.grid(row=0, column=1, sticky='w')
        # check if question is edited or question type is not 'CO'
        if survey_question[ques_id]['is_edited']:  # set default value accordingly, call load_ques_type method
            self.option_value.set(survey_question[ques_id]['question_type'])
            self.load_ques_type()
        else:  # set drop down box default value to 'CO'
            self.option_value.set('CO')

    # load question type from survey question data, then preset question settings accordingly
    def load_ques_type(self):
        # for type 'CO', only display question title, no option cells, no check box, hide add button
        if self.option_value.get() == 'CO':
            # hide add button
            self.option_control.hide_add_button()
            # load question
        # for type 'YN', only display two option cells with text 'Yes' and 'No', 'Reason' check box, hide add button
        elif self.option_value.get() == 'YN':
            # hide add button
            self.option_control.hide_add_button()
            # preset two option cells
            self.option_control.add_option_cell()
            self.option_control.option_list[0].option_entry.insert(0, 'Yes')
            self.option_control.option_list[0].delete_button.destroy()
            self.option_control.add_option_cell()
            self.option_control.option_list[1].option_entry.insert(0, 'No')
            self.option_control.option_list[1].delete_button.destroy()
            # set checker text, display checker
            self.checker_text = 'Reason'
            self.checker = tk.Checkbutton(self.right_frame, text=self.checker_text, variable=self.is_checked)
            self.checker.grid(row=5, column=0, padx=5, pady=10, columnspan=2, sticky='w')
            # load is_checked from question setting data
            if survey_question[self.ques_id]['is_checked'] == '1':
                self.checker.select()
        # for type 'CH', display two empty option cells, show add button, 'Other' check box
        elif self.option_value.get() == 'CH':
            # show add button
            self.option_control.show_add_button()
            # load options from question setting data, then set option cells accordingly
            for index, opt in enumerate(survey_question[self.ques_id]['option']):
                self.option_control.add_option_cell()
                self.option_control.option_list[index].option_entry.insert(0, opt)
            # set checker text, display checker
            self.checker_text = 'Other'
            self.checker = tk.Checkbutton(self.right_frame, text=self.checker_text, variable=self.is_checked)
            self.checker.grid(row=5, column=0, padx=5, pady=10, columnspan=2, sticky='w')
            # load is_checked from question setting data
            if survey_question[self.ques_id]['is_checked'] == '1':
                self.checker.select()
        # for type 'MC', display two empty option cells, show add button, 'Other' check box
        elif self.option_value.get() == 'MC':
            # show add button
            self.option_control.show_add_button()
            # load options from question setting data, then set option cells accordingly
            for index, opt in enumerate(survey_question[self.ques_id]['option']):
                self.option_control.add_option_cell()
                self.option_control.option_list[index].option_entry.insert(0, opt)
            # set checker text, display checker
            self.checker_text = 'Other'
            self.checker = tk.Checkbutton(self.right_frame, text=self.checker_text, variable=self.is_checked)
            self.checker.grid(row=5, column=0, padx=5, pady=10, columnspan=2, sticky='w')
            # load is_checked from question setting data
            if survey_question[self.ques_id]['is_checked'] == '1':
                self.checker.select()
        # for type 'LI', display five option cells with text '1-5', show add button, no check box
        elif self.option_value.get() == 'LI':
            # show add button
            self.ques_type = self.option_value.get()
            # load options from question setting data, then set option cells accordingly
            for index, opt in enumerate(survey_question[self.ques_id]['option']):
                self.option_control.add_option_cell()
                self.option_control.option_list[index].option_entry.insert(0, opt)

    def update_ques_type(self, *args):  # use self.ques_type to record last choice, and get current choice.
        # if current choice equals last choice, nothing happens. otherwise, user would have to retype option text
        # if not equal, check type value and preset option sells accordingly
        if self.option_value.get() != self.ques_type:
            # clean up current on screen option cells
            # first, destroy option cells currently on screen
            for opt in self.option_control.option_list:
                opt.destroy_option_cell()
            # then, clear up option_text and option_list
            self.option_control.option_text.clear()
            self.option_control.option_list.clear()
            # also, destroy current checker
            self.checker.destroy()
            # for type 'CO', only display question title, no option cells, no check box, hide add button
            if self.option_value.get() == 'CO':
                # set last choice value
                self.ques_type = self.option_value.get()
                # hide add button
                self.option_control.hide_add_button()
            # for type 'YN', only display two option cells with text 'Yes' and 'No', 'Reason' check box, hide add button
            elif self.option_value.get() == 'YN':
                # set last choice value
                self.ques_type = self.option_value.get()
                # hide add button
                self.option_control.hide_add_button()
                # preset two option cells
                self.option_control.add_option_cell()
                self.option_control.option_list[0].option_entry.insert(0, 'Yes')
                self.option_control.option_list[0].delete_button.destroy()
                self.option_control.add_option_cell()
                self.option_control.option_list[1].option_entry.insert(0, 'No')
                self.option_control.option_list[1].delete_button.destroy()
                # set checker text, display checker
                self.checker_text = 'Reason'
                self.checker = tk.Checkbutton(self.right_frame, text=self.checker_text, variable=self.is_checked)
                self.checker.grid(row=5, column=0, padx=5, pady=10, columnspan=2, sticky='w')
            # for type 'CH', display two empty option cells, show add button, 'Other' check box
            elif self.option_value.get() == 'CH':
                # set last choice value
                self.ques_type = self.option_value.get()
                # show add button
                self.option_control.show_add_button()
                # preset two option cells
                self.option_control.add_option_cell()
                self.option_control.add_option_cell()
                # set checker text, display checker
                self.checker_text = 'Other'
                self.checker = tk.Checkbutton(self.right_frame, text=self.checker_text, variable=self.is_checked)
                self.checker.grid(row=5, column=0, padx=5, pady=10, columnspan=2, sticky='w')
            # for type 'MC', display two empty option cells, show add button, 'Other' check box
            elif self.option_value.get() == 'MC':
                # set last choice value
                self.ques_type = self.option_value.get()
                # show add button
                self.option_control.show_add_button()
                # preset two option cells
                self.option_control.add_option_cell()
                self.option_control.add_option_cell()
                # set checker text, display checker
                self.checker_text = 'Other'
                self.checker = tk.Checkbutton(self.right_frame, text=self.checker_text, variable=self.is_checked)
                self.checker.grid(row=5, column=0, padx=5, pady=10, columnspan=2, sticky='w')
            # for type 'LI', display five option cells with text '1-5', show add button, no check box
            elif self.option_value.get() == 'LI':
                # set last choice value
                self.option_control.show_add_button()
                # show add button
                self.ques_type = self.option_value.get()
                # preset five option cells
                for i in range(5):
                    self.option_control.add_option_cell()
                    self.option_control.option_list[i].option_entry.insert(0, f'{i + 1}')

    def save_setting(self):
        # save question title to survey question list
        survey_question[self.ques_id]['question_text'] = self.question_entry.get()
        # save question type to survey question list
        survey_question[self.ques_id]['question_type'] = self.option_value.get()
        # clean up previous options in survey question list
        survey_question[self.ques_id]['option'] = []
        # save new options to survey question list
        for opt in self.option_control.option_list:
            survey_question[self.ques_id]['option'].append(opt.option_entry.get())
        # save is_checked to survey question list
        survey_question[self.ques_id]['is_checked'] = str(self.is_checked.get())
        # save note to survey question list
        survey_question[self.ques_id]['note'] = self.notes_input.get()
        # set question is edited
        survey_question[self.ques_id]['is_edited'] = True
        # update page status
        page_control.update_page_status()
        # destroy popup window widget
        self.destroy()
        root.update()
        root.deiconify()

    def delete_ques(self):
        # remove current question from survey_question list
        del survey_question[self.ques_id]
        # update page status, which also updates onscreen cell
        page_control.update_page_status()
        # destroy popup window widget
        self.destroy()
        root.update()
        root.deiconify()

    def close_window(self):
        # destroy popup window widget
        self.destroy()
        root.update()
        root.deiconify()


# define option cell class
class option_cell:

    def __init__(self, control, cell_id):
        # 'control' parameter is the root reference of this class
        self.control = control
        # cell_id is the index of each cell in option list within option_controller class
        self.cell_id = cell_id
        # cell_id starts with 0, option label starts with 1
        self.label_id = cell_id + 1
        self.label = tk.Label(control.root, text=f'Option {self.label_id}')
        self.label.grid(row=cell_id + 1, column=0)
        # input box to type in question text
        self.option_entry = tk.Entry(control.root, width=45)
        self.option_entry.grid(row=cell_id + 1, column=1)
        # delete button
        self.delete_button = tk.Button(control.root, text='X', command=self.delete_option_cell)
        self.delete_button.grid(row=cell_id + 1, column=2)

    # call option_controller to execute update_delete_option method
    def delete_option_cell(self):
        self.control.update_delete_option(self.cell_id)

    # destroy widgets within option_cell
    def destroy_option_cell(self):
        self.label.destroy()
        self.option_entry.destroy()
        self.delete_button.destroy()


# define option manager class
class option_controller:
    add_button = tk.Button()

    def __init__(self, original):
        self.root = original
        self.add_button = tk.Button(self.root, text='Add New Option', height=1, width=20,
                                    command=self.add_option_cell)
        # two variables to store current option cells and text of each option
        self.option_list = []
        self.option_text = []

    # display button
    def show_add_button(self):
        self.add_button.grid(row=13, column=1, padx=10, columnspan=3)

    # hide button
    def hide_add_button(self):
        self.add_button.grid_forget()

    # add a new option cell
    def add_option_cell(self):
        # append an instance of option cell class to option_list, and pass self as reference of root to option manager
        self.option_list.append(option_cell(self, len(self.option_list)))
        # option limit is 10, once it reaches 10 options, call method to hide button
        if len(self.option_list) == 10:
            self.hide_add_button()

    # remove deleted option and save the rest
    def update_delete_option(self, cell_id):
        # first, clear up option_text list
        self.option_text.clear()
        # extract text of each option in current option_list, then append text to option_text list
        for opt in self.option_list:
            self.option_text.append(opt.option_entry.get())
        # remove the text of deleted option from option_text
        del self.option_text[cell_id]
        # destroy option cells currently on screen
        for opt in self.option_list:
            opt.destroy_option_cell()
        # clear up option_list
        self.option_list.clear()
        # according to remaining options in option_text, regenerate option cells and assign option text accordingly
        for index, text in enumerate(self.option_text):
            self.option_list.append(option_cell(self, index))
            self.option_list[index].option_entry.insert(0, text)
        # once option number is less than 10, call show button method
        if len(self.option_list) < 10:
            self.show_add_button()


# define responder class
class responder(tk.Toplevel):

    def __init__(self, original):
        self.original_frame = original
        tk.Toplevel.__init__(self)
        self.transient(root)
        # self.geometry("660x410")
        self.lift()
        self.title('Quiksur-Responder')
        # get control force focus on new window
        self.grab_set()
        # set new window position
        x = root.winfo_x()
        y = root.winfo_y()
        self.geometry("+%d+%d" % (x + 250, y + 150))
        # create variable ques_id
        self.ques_id = 0
        # create widgets for page control
        self.forward = tk.Button(self, text='>>', command=self.button_forward)
        self.backward = tk.Button(self, text='<<', command=self.button_backward)
        self.page_status = tk.Label(self, text=f'{self.ques_id + 1} of {len(survey_question)}')
        self.exit_button = tk.Button(self, text='Exit Survey', padx=5, command=self.button_exit)
        self.lower_frame = tk.Frame()
        self.lower_left = tk.Frame()
        self.lower_right = tk.Frame()
        # create an instance of class enter_ID, let responder enter responder ID
        enter_ID(self)
        # create answer list to store current responder's answer, starting with responder ID
        self.survey_answer = dict()
        # create a list to store widgets of current question
        self.onscreen_widget = []
        # create a list to store input options onscreen
        self.onscreen_option = []

    def update_responder(self):
        # create a labelframe for responder window and show page status
        ID_frame = tk.LabelFrame(self, text=f'{self.ques_id + 1} of {len(survey_question)}', labelanchor='n',
                                 relief='ridge', borderwidth=2, padx=5, pady=5)
        ID_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky='n')
        # separate the ID_frame into upper and lower two invisible frames to sort option entries and drop down menu
        upper_frame = tk.Frame(ID_frame, height=55, width=540, relief='ridge', borderwidth=2)
        upper_frame.grid(row=0, column=0, columnspan=2, sticky='n', padx=5)
        upper_frame.grid_propagate(0)
        # self.lower_frame = tk.Frame(ID_frame, height=300, width=540, relief='ridge', borderwidth=2)
        # self.lower_frame.grid(row=1, column=0, sticky='n', padx=5, pady=5)
        # self.lower_frame.grid_propagate(0)
        self.lower_left = tk.Frame(ID_frame, height=285, width=265, relief='ridge', borderwidth=2)
        self.lower_left.grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.lower_left.grid_propagate(0)
        self.lower_right = tk.Frame(ID_frame, height=285, width=265, relief='ridge', borderwidth=2)
        self.lower_right.grid(row=1, column=1, sticky='e', padx=5, pady=5)
        self.lower_right.grid_propagate(0)
        # wrap text with 80 characters per line to display multi-line text in question title
        label_text = survey_question[self.ques_id]['question_text']
        label_text = textwrap.fill(label_text, width=80)
        ques_title = tk.Label(upper_frame, text=label_text)
        ques_title.grid(sticky='e')
        # update appearance of page buttons
        if self.ques_id == 0:
            if len(survey_question) == 1:
                self.backward = tk.Button(self, text='<<', command=self.button_backward, state=tk.DISABLED)
                self.backward.grid(row=1, column=0, sticky='e')
                self.forward = tk.Button(self, text='>>', command=self.button_forward, state=tk.DISABLED)
                self.forward.grid(row=1, column=2, sticky='w')
            else:
                self.backward = tk.Button(self, text='<<', command=self.button_backward, state=tk.DISABLED)
                self.backward.grid(row=1, column=0, sticky='e')
                self.forward = tk.Button(self, text='>>', command=self.button_forward, state=tk.NORMAL)
                self.forward.grid(row=1, column=2, sticky='w')
        elif self.ques_id == len(survey_question) - 1:
            self.forward = tk.Button(self, text='>>', command=self.button_forward, state=tk.DISABLED)
            self.forward.grid(row=1, column=2, sticky='w')
            self.backward = tk.Button(self, text='<<', command=self.button_backward, state=tk.NORMAL)
            self.backward.grid(row=1, column=0, sticky='e')
        else:
            self.forward = tk.Button(self, text='>>', command=self.button_forward, state=tk.NORMAL)
            self.backward = tk.Button(self, text='<<', command=self.button_backward, state=tk.NORMAL)
            self.forward.grid(row=1, column=2, sticky='w')
            self.backward.grid(row=1, column=0, sticky='e')
        # show exit button
        self.exit_button.grid(row=1, column=1, pady=5)

        # clean up onscreen widgets
        for option in self.onscreen_widget:
            option.destroy()

        # update options
        self.onscreen_option.clear()
        if survey_question[self.ques_id]['question_type'] == 'CO':
            self.onscreen_option.append(answer_input(self, 'Answer:'))
        elif survey_question[self.ques_id]['question_type'] == 'CH':
            self.onscreen_option.append(answer_CH_LI_YN(self, self.ques_id))
            if survey_question[self.ques_id]['is_checked'] == '1':
                self.onscreen_option.append(answer_input(self, 'Other:'))
        elif survey_question[self.ques_id]['question_type'] == 'MC':
            self.onscreen_option.append(answer_MC(self, self.ques_id))
            if survey_question[self.ques_id]['is_checked'] == '1':
                self.onscreen_option.append(answer_input(self, 'Other:'))
        elif survey_question[self.ques_id]['question_type'] == 'YN':
            self.onscreen_option.append(answer_CH_LI_YN(self, self.ques_id))
            if survey_question[self.ques_id]['is_checked'] == '1':
                self.onscreen_option.append(answer_input(self, 'Reason:'))
        elif survey_question[self.ques_id]['question_type'] == 'LI':
            self.onscreen_option.append(answer_CH_LI_YN(self, self.ques_id))
        print(survey_question[self.ques_id]['question_type'], survey_question[self.ques_id]['is_checked'],
              f'onsreen option {len(self.onscreen_option)}')

    def button_forward(self):
        self.save_choice()
        self.ques_id += 1
        self.update_responder()

    def button_backward(self):
        self.save_choice()
        self.ques_id -= 1
        self.update_responder()

    def button_exit(self):
        message_win = messagebox.askyesno('Alert', 'Do you want to save the answers before exit?')
        if message_win == 1:
            print('save results')
            print(self.survey_answer)
            self.save_result()
            self.close_window()
        else:
            print('dont save result')
            self.close_window()

    def save_choice(self):
        # save choice to answer list
        # check question type, then check if input box is checked
        if survey_question[self.ques_id]['is_checked'] == '1':
            if len(self.onscreen_option) == 2:
                self.survey_answer[str(self.ques_id + 1)] = [self.onscreen_option[0].get_result,
                                                             self.onscreen_option[1].get_result]
            else:
                self.survey_answer[str(self.ques_id + 1)] = [self.onscreen_option[0].get_result, '']

        else:
            self.survey_answer[str(self.ques_id + 1)] = [self.onscreen_option[0].get_result]
        print(self.survey_answer)

    def save_result(self):
        # in case it's the last question, save choice of last question before exiting
        self.save_choice()
        # save result to answer_record list
        # check whether there is an existing record of current ID
        check_ID = False
        item = 0
        for index, record in enumerate(answer_record):
            if record['ID'] == self.survey_answer['ID']:
                check_ID = True
                item = index
        # if there is and existing record of current ID, replace with new answer
        if check_ID:
            answer_record[item] = self.survey_answer
        else:   # if not, append new answer
            answer_record.append(self.survey_answer)
        print(len(answer_record), str(answer_record))

    def close_window(self):
        # destroy popup window widget
        self.destroy()
        root.update()
        root.deiconify()


# define answer_CH_LI_YN class
class answer_CH_LI_YN:

    def __init__(self, original, quesid):
        self.button_list = []
        self.variable = tk.IntVar()
        if str(quesid + 1) in original.survey_answer:
            self.variable.set(str(original.survey_answer[str(quesid + 1)][0]))
        for index, option in enumerate(survey_question[quesid]['option']):
            option = textwrap.fill(option, width=40)
            self.button_list.append(tk.Radiobutton(original.lower_left, text=option, variable=self.variable,
                                                   value=index + 1))
        for index, button in enumerate(self.button_list):
            button.grid(row=index, column=0, sticky='w')
            original.onscreen_widget.append(button)

    def get_result(self):
        return self.variable.get()

    def destroy(self):
        for button in self.button_list:
            button.destroy()


# define answer_MC class
class answer_MC:

    def __init__(self, original, quesid):
        self.button_list = []
        self.variable_list = []
        for index, option in enumerate(survey_question[quesid]['option']):
            var = tk.IntVar()
            self.variable_list.append(var)
            option = textwrap.fill(option, width=40)
            self.button_list.append(tk.Checkbutton(original.lower_left, text=option, variable=var))
        if str(quesid + 1) in original.survey_answer:
            for index, option in enumerate(self.button_list):
                if original.survey_answer[str(quesid + 1)][0][index] == 1:
                    option.select()
        for index, button in enumerate(self.button_list):
            button.grid(row=index, column=0, sticky='w')
            original.onscreen_widget.append(button)

    def get_result(self):
        results = [i.get() for i in self.variable_list]
        return results

    def destroy(self):
        for button in self.button_list:
            button.destroy()


# define answer_input class
class answer_input:

    def __init__(self, original, label_text):
        self.answer_label = tk.Label(original.lower_right, text=label_text)
        self.answer_label.grid(sticky='w')
        original.onscreen_widget.append(self.answer_label)
        self.answer_input = tk.Entry(original.lower_right, width=26)
        self.answer_input.grid(padx=5, sticky='w')
        original.onscreen_widget.append(self.answer_input)
        if str(original.ques_id + 1) in original.survey_answer:
            if survey_question[original.ques_id]['question_type'] == 'CO':
                self.answer_input.insert(0, original.survey_answer[str(original.ques_id + 1)][0])
            else:
                self.answer_input.insert(0, original.survey_answer[str(original.ques_id + 1)][1])

    def get_result(self):
        return self.answer_input.get()

    def destroy(self):
        self.answer_label.destroy()
        self.answer_input.destroy()


# define question_note class
class question_note:

    def __init__(self, original, quesid):
        self.note_label = tk.Label(original.lower_right, text='Note:')
        self.note_label.grid(sticky='w')
        label_text = survey_question[quesid]['note']
        label_text = textwrap.fill(label_text, width=40)
        self.note_text = tk.Label(original.lower_right, text=label_text)
        self.note_text.grid(sticky='w')
        original.onscreen_widget.append(self.note_label)
        original.onscreen_widget.append(self.note_text)


# define enter_ID class
class enter_ID:

    def __init__(self, original):
        self.root = original
        # create ID input widgets
        self.label = tk.Label(self.root, text='Please enter you responder ID:')
        self.label.grid(columnspan=2, padx=10, pady=5)
        self.input_box = tk.Entry(self.root)
        self.input_box.grid(columnspan=2)
        self.ok_button = tk.Button(self.root, text='OK', command=self.button_ok)
        self.ok_button.grid(row=2, column=0, sticky='e', padx=10, pady=10)
        self.cancel_button = tk.Button(self.root, text='Cancel', command=self.button_cancel)
        self.cancel_button.grid(row=2, column=1, sticky='w', padx=10, pady=10)

    def button_ok(self):
        if self.input_box.get() == '':
            tk.messagebox.showinfo('Alert', 'Please enter responder ID!')
        else:
            self.root.survey_answer['ID'] = self.input_box.get()
            self.root.update_responder()
            self.label.destroy()
            self.input_box.destroy()
            self.ok_button.destroy()
            self.cancel_button.destroy()
            x = root.winfo_x()
            y = root.winfo_y()
            self.root.geometry("+%d+%d" % (x + 50, y + 20))

    def button_cancel(self):
        self.root.close_window()


# sample item of a new question entry
new_question = {
    'question_type': 'CO',
    'question_text': 'Click Edit button to edit question',
    'is_edited': False,
    'option': [],
    'is_checked': '0',
    'note': ''
}
# content and settings of each question
survey_question = []
# user's answers to each question
answer_record = []
# create an instance of main menu class
menu = main_menu(root)
# create an instance of cell controller class
cell_control = cell_controller(root)
# create an instance of page controller class
page_control = page_controller()

# Keep the program running
root.mainloop()
