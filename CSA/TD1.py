import numpy as np
import matplotlib.pyplot as plt

data = {
    'Dadda_takahashi_TD1': {
        'bit size': [8, 16, 32, 64, 128, 256, 512, 1024],
        't-depth': [77, 125, 221, 413, 797, 1565, 3101, 6173],
        't-count': [428, 812, 1580, 3116, 6188, 12332, 24620, 49196],
        'q-count': [182, 358, 710, 1414, 2822, 5638, 11270, 22534]
    },
    'Wallace_takahashi_TD1': {
        'bit size': [8, 16, 32, 64, 128, 256, 512, 1024],
        't-depth': [49, 97, 193, 385, 769, 1537, 3073, 6145],
        't-count': [392, 816, 1664, 3360, 6752, 13536, 27104, 54240],
        'q-count': [190, 382, 766, 1534, 3070, 6142, 12286, 24574]
    },

    'Dadda_inDraper_TD1': {
        'bit size': [8, 16, 32, 64, 128, 256, 512, 1024],
        't-depth': [71, 89, 113, 131, 149, 167, 185, 203],
        't-count': [806, 1729, 3750, 8093, 17318, 36769, 77582, 162925],
        'q-count': [197, 388, 771, 1538, 3073, 6144, 12287, 24574]
    },
    'Wallace_inDraper_TD1': {
        'bit size': [8, 16, 32, 64, 128, 256, 512, 1024],
        't-depth': [55, 79, 100, 121, 139, 157, 175, 193],
        't-count': [567, 1453, 3463, 7861, 17287, 37245, 79191, 166933],
        'q-count': [198, 404, 818, 1648, 3310, 6636, 13290, 26600]
    },
    'Dadda_outDraper_TD1': {
        'bit size': [8, 16, 32, 64, 128, 256, 512, 1024],
        't-depth': [39, 45, 51, 57, 63, 69, 75, 81],
        't-count': [542, 1081, 2180, 4399, 8858, 17797, 35696, 71515],
        'q-count': [206, 405, 804, 1603, 3202, 6401, 12800, 25599]
    },
    'Wallace_outDraper_TD1': {
        'bit size': [8, 16, 32, 64, 128, 256, 512, 1024],
        't-depth': [31, 38, 44, 50, 56, 62, 68, 74],
        't-count': [443, 1001, 2159, 4517, 9275, 18833, 37991, 76349],
        'q-count': [208, 422, 852, 1714, 3440, 6894, 13804, 27626]
    },
    'Dadda_Wang_Ling_TD1': {
        'bit size': [8, 16, 32, 64, 128, 256, 512, 1024],
        't-depth': [50, 57, 69, 81, 93, 105, 117, 129],
        't-count': [885, 1711, 3405, 6835, 13737, 27583, 55317, 110827],
        'q-count': [264, 518, 1032, 2066, 4140, 8294, 16608, 33242]
    },

    ###



    'Wallace_Wang_Ling_TD1': {
        'bit size': [8, 16, 32, 64, 128, 256, 512, 1024],
        't-depth': [40, 52, 64, 76, 88, 100, 112, 124],
        't-count': [653, 1498, 3251, 6820, 14021, 28486, 57479, 115528],
        'q-count': [241, 508, 1051, 2146, 4345, 8752, 17575, 35230]
    },

    # remaining data...
}
import numpy as np
import matplotlib.pyplot as plt

# Bar width and position setup
barWidth = 0.1
bit_sizes = data['Dadda_takahashi_TD1']['bit size']
positions = [np.arange(len(bit_sizes))]
for _ in range(1, len(data)):
    positions.append([x + barWidth for x in positions[-1]])

# Define custom styles for specific data categories
custom_styles = {
    'Dadda_takahashi_TD1': {'color': '#FF6666'},
    'Dadda_inDraper_TD1': {'color': '#6699FF'},
    'Dadda_outDraper_TD1': {'color': '#66FF66'},
    'Dadda_Wang_Ling_TD1': {'color': '#FF9933'},
    'Wallace_takahashi_TD1': {'color': '#FF9999', 'edgecolor': 'white', 'hatch': '/'},
    'Wallace_inDraper_TD1': {'color': '#99CCFF', 'edgecolor': 'white', 'hatch': '/'},
    'Wallace_outDraper_TD1': {'color': '#99FF99', 'edgecolor': 'white', 'hatch': '/'},
    'Wallace_Wang_Ling_TD1': {'color': '#FFCC66', 'edgecolor': 'white', 'hatch': '/'},
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