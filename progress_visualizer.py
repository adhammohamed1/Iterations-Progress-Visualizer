from typing import Iterable
import math


def _colorize(string, color):
    """
    Colorizes a string for terminal output.

    Parameters:
        string (str): The string to colorize.
        color (str): The color to use.

    Returns:
        str: The colorized string.
    """
    colors = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'pink': '\033[95m',
        'reset': '\033[0m'
    }
    
    if color not in colors:
        raise ValueError(f'Unsupported color: {color}')
    
    return colors[color] + string + colors['reset']


class ProgressVisualizer:
    """
    A class for visualizing the progress of an iterable in the terminal via a progress bar.
    """

    def __init__(
            self, bar_length: int = 50, done_color: str = 'green', progress_color: str = 'magenta'
            ):
        """
        Initializes a progress visualizer.

        Parameters:
            bar_length (int): The length of the progress bar.
            done_color (str): The color of the progress bar when it is done.
            progress_color (str): The color of the progress bar when it is not done.

        Supported colors:
            black, red, green, yellow, blue, magenta, cyan, white, pink
        """
        self.bar_length = bar_length
        self.done_color = done_color
        self.progress_color = progress_color
        self.fill_char = '='
        self.cursor_pos = (None, None)


    def _update_progress_bar(
            self, progress: int, total: int, desc: str
            ):
        """
        Updates a progress bar in the terminal.

        Parameters:
            progress (int): The current progress.
            total (int): The total iterable length.
            desc (str): The description of the operation in progress.
        """
        
        filled = int(math.floor(self.bar_length * progress / float(total)))
        pending = self.bar_length - filled
        perc = round(100 * progress / float(total), 2)

        # Reset the line
        print('\r\033[2K', end='', flush=True)

        # Print the description
        print(f'{desc}:', end=' ')

        # Update the progress bar
        bar_raw = self.fill_char * filled + ' ' * pending
        bar = _colorize(bar_raw, self.progress_color if progress < total else self.done_color)
        print(f'[{bar}]', end=' ') # Print the progress bar

        # Update the progress percentage and count
        text_color = 'reset' if progress < total else self.done_color
        print(_colorize(str(perc)+"%", text_color), end=' ') # Print the progress percentage
        print(_colorize(f'({progress}/{total})', text_color), end=' ', flush=True) # Print the progress count


        print('\033[999C', end='') # Move the cursor to the end of the line

    def _get_current_cursor_pos(self):
        """
        Gets the current cursor position.

        Returns:
            tuple: The current cursor position.
        """
        import sys
        import msvcrt

        # Query the cursor position
        sys.stdout.write('\x1b[6n')
        sys.stdout.flush()

        # Read the response from stdin
        # msvcrt is used to avoid blocking
        buffer = bytes()
        while msvcrt.kbhit():
            buffer += msvcrt.getch()

        # Parse the response
        hex_loc = buffer.decode()
        hex_loc = hex_loc.replace('\x1b[', '').replace('R', '')
        row, col = map(int, hex_loc.split(';'))
        return row, col

    def visualize(
            self, iterable: Iterable, desc: str = 'Progress', fill_char: str = '='
            ):
        """
        Visualizes the progress of an iterable.

        Parameters:
            iterable (Iterable): The iterable to visualize.
        """
        if len(fill_char) != 1:
            raise ValueError('The fill character must be a single character.')
        self.fill_char = fill_char
        
        self.cursor_pos = self._get_current_cursor_pos()
        total = len(iterable)

        for i, item in enumerate(iterable):

            # Save the cursor position prior to updating the progress bar
            if i > 0:
                pre_progress_bar_cursor_pos = self._get_current_cursor_pos()
            else:
                pre_progress_bar_cursor_pos = (self.cursor_pos[0]+1, self.cursor_pos[1])

            # Restore the cursor to the position of the progress bar
            print('\033[{};{}H'.format(*self.cursor_pos), end='')
            self._update_progress_bar(i+1, total, desc)

            # Restore the cursor position prior to updating the progress bar
            print('\033[{};{}H'.format(*pre_progress_bar_cursor_pos), end='')

            yield item
        

# Example usage
if __name__ == '__main__':
    pv = ProgressVisualizer()
    my_list = [i for i in range(10001)]

    for item in pv.visualize(my_list):
        if item % 1000 == 0:
            print(item)

    print('Done!')
