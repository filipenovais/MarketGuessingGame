import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from tkinter import IntVar
import matplotlib.dates as mdates
import warnings
from download_funcs import download_symbol
import pickle

DATA_PATH = "data/"

class MarketGuessingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Market Guessing Game")

        self.total_tries = 0
        self.right_tries = 0


        # 000000000000000 Left Section (Inputs) 000000000000000
        left_frame = ttk.Frame(root)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # High Score
        pickle_high_score_path = DATA_PATH+'high_score'
        if os.path.exists(pickle_high_score_path):
            with open(pickle_high_score_path, 'rb') as file:
                high_score = pickle.load(file)
            self.hight_score = int(high_score.split(" ")[0])
        else:
            high_score = "0 / 0"
            with open(pickle_high_score_path, 'wb') as file:
                pickle.dump(high_score, file)
            self.hight_score = 0

        # High Score label
        self.hight_score_label = ttk.Label(left_frame, text=f"High Score:  {high_score}", font="TkDefaultFont 12 bold")
        self.hight_score_label.grid(row=0, column=0, pady=(5, 5), sticky=tk.W)

        # DOWNLOAD entry
        self.download_label = ttk.Label(left_frame, text="Download Market Symbol:")
        self.download_label.grid(row=1, column=0, pady=(5, 5), sticky=tk.W)
        self.download_entry = ttk.Entry(left_frame)
        self.download_entry.grid(row=1, column=1, pady=(5, 5), padx=(15, 0), sticky=tk.W)
        self.download_entry.insert(0, "BTCUSDT_1d")
        
        # DOWNLOAD button
        self.download_button = ttk.Button(left_frame, text="Download Data", command=self.download_data)
        self.download_button.grid(row=2, column=1, columnspan=1, pady=10)
        
        # DOWNLOAD status
        self.download_status = ttk.Label(left_frame, text="             ---", font="TkDefaultFont 10 bold")
        self.download_status.grid(row=2, column=0, pady=(5, 5), padx=(15, 0), columnspan=1, sticky=tk.W)

        # SEPERATOR
        self.seperator_label = ttk.Label(left_frame, text="                                    ------------------------------")
        self.seperator_label.grid(row=3, column=0, columnspan=2, pady=(5, 5), sticky=tk.W)

        # Directory selection
        self.directory_label = ttk.Label(left_frame, text="Select CSV file:")
        self.directory_label.grid(row=4, column=0, pady=(0, 5), sticky=tk.W)
        self.directory_combobox = ttk.Combobox(left_frame, state="readonly", values=self.get_csv_files())
        self.directory_combobox.grid(row=4, column=1, pady=(0, 5), padx=(15, 0), sticky=tk.W)
        self.directory_combobox.config(width=17)
        self.directory_combobox.set("BTCUSDT_1d.csv")

        # Lookback and forward selection
        self.days_label = ttk.Label(left_frame, text="Nº Candles - Look Back:")
        self.days_label.grid(row=5, column=0, pady=(5, 5), sticky=tk.W)
        self.days_spinbox = ttk.Spinbox(left_frame, from_=1, to=1000)
        self.days_spinbox.grid(row=5, column=1, pady=(5, 5), padx=(15, 0), sticky=tk.W)
        self.days_spinbox.config(width=18)
        self.days_spinbox.set(60)
        self.range_label = ttk.Label(left_frame, text="Nº Candles - Guess:")
        self.range_label.grid(row=6, column=0, pady=(5, 5), sticky=tk.W)
        self.range_spinbox = ttk.Spinbox(left_frame, from_=1, to=1000)
        self.range_spinbox.grid(row=6, column=1, pady=(5, 5), padx=(15, 0), sticky=tk.W)
        self.range_spinbox.config(width=18)
        self.range_spinbox.set(3)

        # Date from to
        self.date_from = ttk.Label(left_frame, text="Guess date FROM:  (YYYY-MM-DD)")
        self.date_from.grid(row=7, column=0, pady=(5, 5), sticky=tk.W)
        self.date_from_entry = ttk.Entry(left_frame)
        self.date_from_entry.grid(row=7, column=1, pady=(5, 5), padx=(15, 0), sticky=tk.W)
        self.date_to = ttk.Label(left_frame, text="Guess date TO:        (YYYY-MM-DD)")
        self.date_to.grid(row=8, column=0, pady=(5, 5), sticky=tk.W)
        self.date_to_entry = ttk.Entry(left_frame)
        self.date_to_entry.grid(row=8, column=1, pady=(5, 5), padx=(15, 0), sticky=tk.W)

        # Checkbox fake prices
        self.custom_line_var = IntVar()
        self.price_checkbox = ttk.Checkbutton(left_frame, text="Show Real Price", variable=self.custom_line_var)
        self.price_checkbox.grid(row=9, column=1, columnspan=2, pady=(5, 5), padx=(15, 0), sticky=tk.W)

        # Load Button
        self.load_data_button = ttk.Button(left_frame, text="Load Data", command=self.load_data)
        self.load_data_button.grid(row=10, column=0, columnspan=2, pady=10)

        # Guess input text
        self.guess_label = ttk.Label(left_frame, text="Select your Guess:")
        self.guess_label.grid(row=11, column=0, pady=(0, 5), sticky=tk.W)

        # Checkbuttons for mutually exclusive selection (Up or Down Movement)
        self.movement_var = IntVar()
        self.up_movement_checkbox = ttk.Radiobutton(left_frame, text="Up Movement", variable=self.movement_var, value=1)
        self.up_movement_checkbox.grid(row=11, column=1, columnspan=1, pady=(5, 5), padx=(15, 0), sticky=tk.W)
        self.down_movement_checkbox = ttk.Radiobutton(left_frame, text="Down Movement", variable=self.movement_var, value=2)
        self.down_movement_checkbox.grid(row=12, column=1, columnspan=1, pady=(5, 5), padx=(15, 0), sticky=tk.W)

        # Make Guess button
        #self.guess_button = ttk.Button(left_frame, text="Make Guess", command=self.make_guess, state=tk.DISABLED)
        self.guess_button = ttk.Button(left_frame, text="Make Guess", command=self.make_guess)
        self.guess_button.grid(row=13, column=1, columnspan=1, pady=10)

        # Next button
        self.guess_button = ttk.Button(left_frame, text="Next", command=self.load_data)
        self.guess_button.grid(row=13, column=0, columnspan=1, pady=10)

        # Result text
        self.dates_label1 = ttk.Label(left_frame, text="")
        self.dates_label1.grid(row=14, column=0, columnspan=2, padx=0)
        self.dates_label2 = ttk.Label(left_frame, text="")
        self.dates_label2.grid(row=15, column=0, columnspan=2, padx=(4,0))
        self.pct_label = ttk.Label(left_frame, text="")
        self.pct_label.grid(row=16, column=0, columnspan=2)
        self.result_label = ttk.Label(left_frame, text=" ", font="TkDefaultFont 15")
        self.result_label.grid(row=17, column=0, columnspan=2)

        # SCORE text
        self.score_label = ttk.Label(left_frame, text="SCORE: ( 0 / 0 )")
        self.score_label.grid(row=18, column=1, columnspan=1)

        # Reset Button
        self.guess_button = ttk.Button(left_frame, text="Reset", command=self.reset)
        self.guess_button.grid(row=18, column=0, columnspan=1, pady=10)

        # 000000000000000 Right Section (Candlestick Chart) 000000000000000
        right_frame = ttk.Frame(root)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        # Create a Figure instance with the desired figsize
        self.fig = plt.Figure(figsize=(9, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Add navigation toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, right_frame)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Get CSV files in the DATA_PATH directory
    def get_csv_files(self):
        csv_files = [file for file in os.listdir(DATA_PATH) if file.endswith('.csv')]
        return csv_files
    
    # Reset score
    def reset(self):
        try:
            self.total_tries = 0
            self.right_tries = 0
            self.score_label.config(text=f"SCORE: ( {self.right_tries} / {self.total_tries} )")
        except Exception as e:
            messagebox.showerror("Error", f"Error reseting: {e}")

    # Download data from selected symbol
    def download_data(self):
        try:
            symbol = self.download_entry.get().split("_")[0]
            interval = self.download_entry.get().split("_")[1]
            download_symbol(symbol, interval, 100000, DATA_PATH)
            self.directory_combobox['values'] = self.get_csv_files()
            self.download_status.config(text="      COMPLETE")
        except Exception as e:
            messagebox.showerror("Error", f"Error downloading data: {e}")
        

    def load_data(self):
        try:
            # Guess variable
            self.guess_played = 0

            # Check if directory is selected
            selected_directory = self.directory_combobox.get()
            if not selected_directory or selected_directory == "Select Directory":
                messagebox.showwarning("Warning", "Please select a valid directory.")
                return
            # Load Dataframe
            file_path = os.path.join(DATA_PATH, selected_directory)
            self.data = pd.read_csv(file_path, parse_dates=True, index_col=0)

            # Select a random datetime and get the selected number of days
            selected_lookback = int(self.days_spinbox.get())            
            selected_guess = int(self.range_spinbox.get())

            # Slice dataframe if necessary
            from_date = self.date_from_entry.get()
            to_date = self.date_to_entry.get()
            if from_date:
                from_date = pd.to_datetime(from_date)
                index_of_desired_date = self.data.index.get_loc(from_date)
                self.data = self.data.iloc[index_of_desired_date-selected_lookback:]
            if to_date:
                to_date = pd.to_datetime(to_date)
                index_of_desired_date = self.data.index.get_loc(to_date)
                self.data = self.data.iloc[:index_of_desired_date+selected_guess]

            # Select random point to start in the dataframe
            random_index = random.randint(selected_lookback, len(self.data) -  selected_guess)
            self.lookback_data = self.data.iloc[random_index - selected_lookback:random_index]
            self.guess_data = self.data.iloc[random_index:random_index + selected_guess]
            self.all_data = self.data.iloc[random_index - selected_lookback:random_index + selected_guess]

            # Change price value
            random_price = 1 if self.custom_line_var.get() else 0.01*self.lookback_data.min().min()*(1-np.random.random()*0.1)
            self.lookback_data = self.lookback_data/random_price

            # Plot the candlestick chart with lookback_data
            self.plot_candlestick(self.lookback_data, selected_guess)
            
            # Erase labels
            self.guess_button.config(state=tk.NORMAL)
            self.pct_label.config(text="")
            self.dates_label1.config(text="")
            self.dates_label2.config(text="")
            self.result_label.config(text="")
            self.download_status.config(text="             ---")

        except Exception as e:
            messagebox.showerror("Error", f"Error loading data: {e}")

    def plot_candlestick(self, data, white_timestamps=0):
        # Clear the existing plot
        self.ax.clear()

        # X axis
        if white_timestamps == 0:
            last_n_points = len(self.guess_data)
            line_x = list(range(len(data)-last_n_points, len(data)))
            line_y = data['Close'].values[-last_n_points:]
            colorline = 'red' if line_y[0]>line_y[-1] else 'green'
            self.ax.plot(line_x, line_y, color=colorline, linestyle='-', linewidth=2, label='Custom Line', alpha=1)
            self.ax.axvline(x=len(data)-last_n_points-0.5, color='black', linestyle='--')

            plot_index = self.all_data.index.strftime('%Y-%m-%d')
            self.ax.set_xticks(range(len(self.all_data)))
            self.ax.set_xticklabels(list(plot_index), rotation=20, ha='center')
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=UserWarning)
                self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        else:
            plot_index = list(range(len(data)))
            plot_index.extend(range(len(data), len(data) + white_timestamps))
            self.ax.set_xticklabels([])
        self.ax.set_xlim(-1, len(plot_index))

        # Plot candlestick chart
        for i, (date, row) in enumerate(data.iterrows()):
            open_price, high, low, close_price = row['Open'], row['High'], row['Low'], row['Close']
            color_body = 'green' if close_price >= open_price else 'red'
            
            if close_price >= open_price:
                color_body = 'green'
                # Plotting candlestick wicks
                self.ax.plot([i, i], [low, open_price], color='black', alpha=0.7)  # Lower wick
                self.ax.plot([i, i], [close_price, high], color='black', alpha=0.7)  # Upper wick
            else:
                color_body = 'red'
                # Plotting candlestick wicks
                self.ax.plot([i, i], [close_price, low], color='black', alpha=0.7)  # Lower wick
                self.ax.plot([i, i], [high, open_price], color='black', alpha=0.7)  # Upper wick

            # Plotting candlestick body
            rectangle = plt.Rectangle((i - 0.4, open_price), 0.8, close_price - open_price, fill=True, color=color_body, alpha=0.7)
            self.ax.add_patch(rectangle)
            rectangle.set_edgecolor('black')

        # Plot Title
        csv_file = self.directory_combobox.get().split('_')
        market = csv_file[0]
        time_frequency = csv_file[1].replace(".csv", "")
        self.ax.set_title(f'Time Frequency: {time_frequency}\nMarket Symbol: {market}')
        

        plt.tight_layout()
        self.canvas.draw()

    def make_guess(self):
        try:
            # Validate that a movement is selected
            if self.movement_var.get() == 0:
                messagebox.showwarning("Warning", "Please select a movement (Up or Down).")
                return
            elif self.guess_played:
                messagebox.showwarning("Info", "Load another guess")
                return

            # Guess variable
            self.guess_played = 1

            # Update the plot with guess_data
            self.plot_candlestick(self.all_data)
            percentage_difference = ((self.guess_data['Close'].iloc[-1] - self.guess_data['Open'].iloc[0]) / self.guess_data['Open'].iloc[0]) * 100

            # Calculate the percentage difference based on the selected movement
            if self.movement_var.get() == 1 and percentage_difference>0:  # Up Movement
                answer = "CORRECT"
                color_answer = 'green'
                self.right_tries += 1
            elif self.movement_var.get() == 2 and percentage_difference<0:  # Down Movement
                answer = "CORRECT"
                color_answer = 'green'
                self.right_tries += 1
            else:
                answer = "WRONG"
                color_answer = 'red'
            self.total_tries += 1

            # Display the result
            pct_text = f"Percentage Change:   {percentage_difference:.2f} %"
            self.pct_label.config(text=pct_text)
            self.result_label.config(text=answer, foreground=color_answer, font="TkDefaultFont 15")
            self.score_label.config(text=f"SCORE: ( {self.right_tries} / {self.total_tries} )", font="TkDefaultFont 10 bold")
            self.dates_label1.config(text=f"from: {self.guess_data.index[0]} (OPEN)")
            self.dates_label2.config(text=f"to:      {self.guess_data.index[-1]} (CLOSE)")

            # Change High Score
            if self.right_tries > self.hight_score:
                score_to_save = f"{self.right_tries} / {self.total_tries}"
                with open(DATA_PATH+'high_score', 'wb') as file:
                    pickle.dump(score_to_save, file)
                self.hight_score = self.right_tries
                self.dates_label2.config(text=f"to:      {self.guess_data.index[-1]} (CLOSE)")
                self.hight_score_label.config(text=f"High Score:  {score_to_save}", font="TkDefaultFont 12 bold")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error making guess: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    game = MarketGuessingGame(root)
    root.mainloop()
