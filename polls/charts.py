import matplotlib.pyplot as plt
from polls import poll_database


def get_pie_chart(connection, options: str, poll_id: int):
    """Creates pie graph with each part based on the amount of votes each option has"""

    title = poll_database.get_poll_title(connection, poll_id)

    figure = plt.figure(figsize=(10, 10))
    axes = figure.add_subplot(1, 1, 1)
    axes.pie(
        [option[1] for option in options],
        labels=[option[0] for option in options],
        autopct="%1.1f%%"
    )
    axes.set_title(title)
    return figure


def create_polls_bar_chart(polls: str):
    """Creates a bar graph based on the amount of votes each poll has"""

    figure = plt.figure(figsize=(8, 5))
    figure.subplots_adjust(bottom=0.2)
    axes = figure.add_subplot(1, 1, 1)
    axes.set_title("Poll Vote Counts")
    axes.set_xlabel("Polls")
    axes.set_xlabel("Number of votes per poll")
    axes.bar(
        range(len(polls)),
        [poll[1] for poll in polls],
        tick_label=[poll[0] for poll in polls]
    )
    plt.xticks(rotation=20, ha="right")
    return figure
