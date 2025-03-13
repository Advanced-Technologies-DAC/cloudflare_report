"""
V4 functions neccesary to create graphs
"""

__version__ = "4.1.0"

import os

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.table import Table
from matplotlib.transforms import Bbox


def format_stat(value: float, stat_type: str) -> str:
    """
    Formats the statistic value based on its type.
    - "numeric" -> Format in K/M (e.g., "12.3K").
    - "byte" -> Convert bytes to MB/GB and format accordingly.

    Args:
        value (float): The total value to format.
        stat_type (str): The type of metric ("numeric" or "byte").

    Returns:
        str: Formatted string representation.
    """
    if stat_type == "numeric":
        return f"{value / 1000:.1f}K"
    elif stat_type == "byte":
        return f"{value / (1024**2):.1f} MB"
    return str(value)


def dashboard_stat_graph(
    first_stat: dict, second_stat: dict, third_stat_title: str, y_label_info: str
) -> None:
    """
    Creates a panel with stats and timeseries:
    - General Stats: Displays title & summary of the stat for the time period.
    - Time Series: Trend over time for two related statistics.

    Args:
        first_stat (dict): Contains title, metric dictionary, and type for the first stat.
        second_stat (dict): Contains title, metric dictionary, and type for the second stat.
        third_stat_title (str): Self explanatory.
        y_label_info (str): Label for the Y-axis of the line chart.

    Returns:
        None: Displays the generated plot.
    """
    fig, axs = plt.subplots(
        2, 1, gridspec_kw={"height_ratios": [1, 4]}, figsize=(10, 6)
    )

    # Totals & format
    total_first = sum(first_stat["content"].values())
    total_second = sum(second_stat["content"].values())
    total_third = total_first - total_second
    formatted_first = format_stat(total_first, first_stat["type"])
    formatted_second = format_stat(total_second, second_stat["type"])
    formatted_third = format_stat(total_third, first_stat["type"])
    stats = [
        (first_stat["title"], formatted_first),
        (second_stat["title"], formatted_second),
        (third_stat_title, formatted_third),
    ]

    # Stats
    for idx, (title, value) in enumerate(stats):
        axs[0].text(
            (idx + 0.5) / 3,
            0.6,
            title,
            ha="center",
            va="center",
            fontsize=12,
            fontweight="normal",
        )
        axs[0].text(
            (idx + 0.5) / 3,
            0.4,
            value,
            ha="center",
            va="center",
            fontsize=14,
            fontweight="bold",
        )
    axs[0].axis("off")

    # Line graph
    colors = ["#3CB5AE", "#A8DADC", "#D9D9D9"]
    dates = list(first_stat["content"].keys())
    values1 = list(first_stat["content"].values())
    values2 = list(second_stat["content"].values())
    axs[1].plot(
        dates,
        values1,
        linestyle="-",
        color=colors[0],
        zorder=3,
        label=first_stat["title"],
    )
    axs[1].fill_between(dates, values1, color=colors[0])
    axs[1].plot(
        dates,
        values2,
        linestyle="-",
        color=colors[1],
        label=second_stat["title"],
    )
    axs[1].fill_between(dates, values2, color=colors[1])

    axs[1].legend(loc="upper left", frameon=False)

    # Standard Y-Axis Formatting
    axs[1].spines["top"].set_visible(False)
    axs[1].spines["right"].set_visible(False)
    axs[1].spines["bottom"].set_color(colors[2])
    axs[1].spines["left"].set_color(colors[2])
    axs[1].set_ylabel(y_label_info, fontsize=12)
    if first_stat["type"] == "byte":
        axs[1].set_ylim(bottom=0)  # Ensure no negative values
        axs[1].set_yticks(axs[1].get_yticks())
        axs[1].set_yticklabels(
            [f"{int(y / 1_048_576)} MB" for y in axs[1].get_yticks()]
        )
    else:
        axs[1].set_yticklabels([f"{int(y):,}" for y in axs[1].get_yticks()])
    plt.xticks()
    plt.tight_layout()
    # plt.show()
    # Save the plot
    plt.savefig("test.png", dpi=300, bbox_inches="tight")
    plt.close()


def dashboard_pie_bar(
    http_versions: dict, ssl_versions: dict, content_types: dict
) -> None:
    """
    Creates a panel with two pie charts and a horizontal bar chart:
    - Pie Chart 1: Top 3 HTTP versions used
    - Pie Chart 2: Top 3 SSL versions used
    - Bar Chart: Types of content delivered (smaller height).

    Args:
        http_versions (dict): Dictionary containing title, metric dictionary, and type.
        ssl_versions (dict): Dictionary containing title, metric dictionary, and type.
        content_types (dict): Dictionary containing title, metric dictionary, and type.

    Returns:
        None: Displays the generated plot.
    """
    fig, axs = plt.subplots(
        1, 3, figsize=(12, 3.5), gridspec_kw={"width_ratios": [1, 1, 0.7]}
    )
    colors = ["#3CB5AE", "#A8DADC", "#5271FF"]

    # Extract titles
    http_title = http_versions["title"]
    ssl_title = ssl_versions["title"]
    content_title = content_types["title"]

    # Extract metric values
    http_metrics = http_versions["content"]
    ssl_metrics = ssl_versions["content"]
    content_metrics = content_types["content"]

    # Pie Chart 1 - HTTP Versions (Top 3)
    sorted_http = sorted(http_metrics.items(), key=lambda x: x[1], reverse=True)[:3]
    http_labels, http_sizes = zip(*sorted_http)
    axs[0].pie(
        http_sizes,
        labels=http_labels,
        autopct=lambda p: f"{int(p)}%",
        startangle=140,
        colors=colors,
    )
    axs[0].set_title(http_title)

    # Pie Chart 2 - SSL Versions (Top 3)
    sorted_ssl = sorted(ssl_metrics.items(), key=lambda x: x[1], reverse=True)[:3]
    ssl_labels, ssl_sizes = zip(*sorted_ssl)
    axs[1].pie(
        ssl_sizes,
        labels=ssl_labels,
        autopct=lambda p: f"{int(p)}%",
        startangle=140,
        colors=colors,
    )
    axs[1].set_title(ssl_title)

    # Bar chart - Content Types
    sorted_items = sorted(content_metrics.items(), key=lambda x: x[1], reverse=True)
    content_labels, content_sizes = zip(*sorted_items)
    y_positions = np.arange(len(content_labels))
    axs[2].barh(y_positions, content_sizes, color=colors[0], height=0.8)
    axs[2].set_title(content_title)
    axs[2].set_yticks([])
    axs[2].set_xticks([])
    axs[2].spines["top"].set_visible(False)
    axs[2].spines["right"].set_visible(False)
    axs[2].spines["bottom"].set_visible(False)
    axs[2].spines["left"].set_visible(False)
    for index, value in enumerate(content_sizes):
        axs[2].text(
            value + max(content_sizes) * 0.02,
            y_positions[index],
            f"{content_labels[index]}: {value:,}",
            va="center",
            fontsize=10,
        )
    plt.tight_layout()
    # plt.show()
    # Save the plot
    plt.savefig("test.png", dpi=300, bbox_inches="tight")
    plt.close()


def dashboard_table_map(first_stat: dict) -> None:
    """
    Creates a panel with a table displaying the top 10 countries by requests and a world map.
    The world map shades countries based on the number of requests.
    Args:
        first_stat (dict): Dictionary with:
            - "title" (str): Title of the stat.
            - "metrics" (dict): Keys are country codes and values are request counts.
    Returns:
        None: Displays the generated plot.
    """
    request_data = first_stat["content"]

    fig, axs = plt.subplots(1, 2, figsize=(12, 6), gridspec_kw={"width_ratios": [1, 4]})

    # Table
    sorted_data = sorted(request_data.items(), key=lambda x: x[1], reverse=True)[:10]
    countries, requests = zip(*sorted_data)
    colors = ["#D9D9D9", "Greens"]

    axs[0].axis("off")
    table = Table(axs[0], bbox=Bbox.from_extents(0, 0, 1, 1))
    headers = ["Country", "Requests"]
    cell_width, cell_height = 1, 3
    for col_idx, header in enumerate(headers):
        table.add_cell(
            0,
            col_idx,
            width=cell_width,
            height=cell_height,
            text=header,
            loc="center",
            facecolor=colors[0],
        )
    for row_idx, (country, request) in enumerate(zip(countries, requests), start=1):
        table.add_cell(
            row_idx,
            0,
            width=cell_width,
            height=cell_height,
            text=country,
            loc="center",
        )
        table.add_cell(
            row_idx,
            1,
            width=cell_width,
            height=cell_height,
            text=f"{request:,}",
            loc="center",
        )
    axs[0].add_table(table)

    # Map
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shapefile_path = os.path.join(
        project_root, "assets", "countries", "ne_110m_admin_0_countries.shp"
    )
    if not os.path.exists(shapefile_path):
        raise FileNotFoundError(f"Shapefile not found: {shapefile_path}")
    world = gpd.read_file(shapefile_path)
    if not os.path.exists(shapefile_path):
        raise FileNotFoundError(f"Shapefile not found: {shapefile_path}")
    world = gpd.read_file(shapefile_path)
    if "ISO_A2" not in world.columns:
        raise KeyError("Shapefile must contain an ISO_A2 column for country codes.")
    world["requests"] = world["ISO_A2"].map(request_data).fillna(0)
    axs[1].set_aspect(5)
    world.plot(column="requests", cmap=colors[1], ax=axs[1])
    world.boundary.plot(ax=axs[1], linewidth=0.1, color="black")
    axs[1].spines["top"].set_visible(False)
    axs[1].spines["right"].set_visible(False)
    axs[1].spines["left"].set_visible(False)
    axs[1].spines["bottom"].set_visible(False)
    axs[1].set_xticks([])
    axs[1].set_yticks([])
    # plt.show()
    # Save the plot
    plt.savefig("test.png", dpi=300, bbox_inches="tight")
    plt.close()


# SOLO TEST
def dashboard_stat_test(stat: dict, y_label_info: str) -> None:
    """
    Creates a panel with stats and a timeseries:
    - General Stats: Displays total, max, and min for the period.
    - Time Series: Trend over time.

    Args:
        stat (dict): Contains title, metric dictionary, and type.
        y_label_info (str): Label for the Y-axis of the line chart.

    Returns:
        None: Displays the generated plot.
    """
    fig, axs = plt.subplots(
        2, 1, gridspec_kw={"height_ratios": [1, 4]}, figsize=(10, 6)
    )

    # Compute statistics
    total = sum(stat["content"].values())
    max_value = max(stat["content"].values())
    min_value = min(stat["content"].values())

    formatted_total = format_stat(total, stat["type"])
    formatted_max = format_stat(max_value, stat["type"])
    formatted_min = format_stat(min_value, stat["type"])

    stats = [
        (stat["title"], formatted_total),
        ("Max", formatted_max),
        ("Min", formatted_min),
    ]

    # Display Stats
    for idx, (title, value) in enumerate(stats):
        axs[0].text(
            (idx + 0.5) / 3,
            0.6,
            title,
            ha="center",
            va="center",
            fontsize=12,
            fontweight="normal",
        )
        axs[0].text(
            (idx + 0.5) / 3,
            0.4,
            value,
            ha="center",
            va="center",
            fontsize=14,
            fontweight="bold",
        )
    axs[0].axis("off")

    # Line graph
    colors = ["#3CB5AE", "#A8DADC", "#D9D9D9"]
    dates = list(stat["content"].keys())
    values = list(stat["content"].values())

    axs[1].plot(
        dates, values, linestyle="-", color=colors[0], zorder=3, label=stat["title"]
    )
    axs[1].fill_between(dates, values, color=colors[0])

    axs[1].legend(loc="upper left", frameon=False)

    # Standard Y-Axis Formatting
    axs[1].spines["top"].set_visible(False)
    axs[1].spines["right"].set_visible(False)
    axs[1].spines["bottom"].set_color(colors[2])
    axs[1].spines["left"].set_color(colors[2])
    axs[1].set_ylabel(y_label_info, fontsize=12)

    if stat["type"] == "byte":
        axs[1].set_ylim(bottom=0)  # Ensure no negative values
        axs[1].set_yticks(axs[1].get_yticks())
        axs[1].set_yticklabels(
            [f"{int(y / 1_048_576)} MB" for y in axs[1].get_yticks()]
        )
    else:
        axs[1].set_yticklabels([f"{int(y):,}" for y in axs[1].get_yticks()])

    plt.xticks()
    plt.tight_layout()
    plt.savefig("test.png", dpi=300, bbox_inches="tight")
    plt.close()
