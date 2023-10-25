import numpy as np
import matplotlib.pyplot as plt

data = {
    'Dadda_gidney': {
        'bit size': [8, 16, 32, 64, 128, 256, 512, 1024],
        't-depth': [24, 32, 48, 80, 144, 272, 528, 1040],
        't-count': [335, 647, 1271, 2519, 5015, 10007, 19991, 39959],
        'q-count': [202, 394, 778, 1546, 3082, 6154, 12298, 24586]
    },
    'Wallace_gidney': {
        'bit size': [8, 16, 32, 64, 128, 256, 512, 1024],
        't-depth': [17, 25, 41, 73, 137, 265, 521, 1033],
        't-count': [335, 687, 1391, 2799, 5615, 11247, 22511, 45039],
        'q-count': [202, 410, 826, 1658, 3322, 6650, 13306, 26618]
    },
    'Dadda_inDraper_TD2': {
        'bit size': [8, 16, 32, 64, 128, 256, 512, 1024],
        't-depth': [28, 32, 36, 40, 44, 49, 54, 59],
        't-count': [530, 1062, 2146, 4334, 8730, 17542, 35186, 70494],
        'q-count': [280, 560, 1128, 2272, 4568, 9168, 18376, 36800]
    },
    'Wallace_inDraper_TD2': {
        'bit size': [8, 16, 32, 64, 128, 256, 512, 1024],
        't-depth': [21, 26, 30, 34, 38, 43, 48, 53],
        't-count': [430, 982, 2126, 4454, 9150, 18582, 37486, 75334],
        'q-count': [240, 528, 1120, 2320, 4736, 9584, 19296, 38736]
    },
    'Dadda_outDraper_TD2': {
        'bit size': [8, 16, 32, 64, 128, 256, 512, 1024],
        't-depth': [24, 27, 30, 33, 36, 39, 42, 45],
        't-count': [434, 856, 1710, 3428, 6874, 13776, 27590, 55228],
        'q-count': [241, 477, 953, 1909, 3825, 7661, 15337, 30693]
    },




    'Wallace_outDraper_TD2': {
        'bit size': [8, 16, 32, 64, 128, 256, 512, 1024],
        't-depth': [17, 21, 24, 27, 30, 33, 36, 39],
        't-count': [388, 840, 1764, 3632, 7388, 14920, 30004, 60192],
        'q-count': [226, 474, 978, 1994, 4034, 8122, 16306, 32682]
    },


    # remaining data...
}

import numpy as np
import matplotlib.pyplot as plt

# Bar width and position setup
barWidth = 0.1
bit_sizes = data['Dadda_gidney']['bit size']
positions = [np.arange(len(bit_sizes))]
for _ in range(1, len(data)):
    positions.append([x + barWidth for x in positions[-1]])

# Define custom styles for specific data categories
custom_styles = {
    'Dadda_gidney': {'color': '#FF6666'},
    'Dadda_inDraper_TD2': {'color': '#3399FF'},
    'Dadda_outDraper_TD2': {'color': '#66FF66'},
    'Wallace_gidney': {'color': '#FF9999', 'edgecolor': 'white', 'hatch': '/'},
    'Wallace_inDraper_TD2': {'color': '#99CCFF', 'edgecolor': 'white', 'hatch': '/'},
    'Wallace_outDraper_TD2': {'color': '#99FF99', 'edgecolor': 'white', 'hatch': '/'},
}

# Plotting function
def plot_data(y_label, value_key, filename):
    plt.figure(figsize=(15, 4))  # Adjust figure size

    # Create bar plots for each data category
    for idx, (key, value) in enumerate(data.items()):
        style = custom_styles.get(key, {})
        plt.bar(positions[idx], value[value_key], width=barWidth, label=key, **style)

    # Set y-axis to logarithmic scale
    plt.yscale('log')

    # General layout adjustments
    plt.xlabel('Bit size', fontweight='bold', fontsize=16)
    plt.ylabel(y_label, fontweight='bold', fontsize=16)
    plt.xticks([r + barWidth * (len(data) / 2) for r in range(len(bit_sizes))], bit_sizes, fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=12)  # Adjusted legend positioning to avoid overlap
    plt.tight_layout()

    # Save the figure as a PNG image
    plt.savefig(y_label+".png", format='png', dpi=600)  # Ensure tight bounding box
    plt.show()

# Plot t-depth
plot_data('t-depth', 't-depth', 't-depth.png')

# Plot t-count
plot_data('t-count', 't-count', 't-count.png')

# Plot q-count
plot_data('q-count', 'q-count', 'q-count.png')