import numpy as np

from image_stats import calculate_gray_stats


def test_calculate_gray_stats_counts_saturated_pixels():
    image = np.array(
        [
            [0, 128, 255],
            [255, 64, 32],
        ],
        dtype=np.uint8,
    )

    stats = calculate_gray_stats(image)

    assert stats["width"] == 3
    assert stats["height"] == 2
    assert stats["mean_gray"] == 122.33
    assert stats["min_gray"] == 0
    assert stats["max_gray"] == 255
    assert stats["overexposed_pixels"] == 2
    assert stats["overexposed_ratio"] == 33.33
