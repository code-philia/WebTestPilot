import cv2
import numpy as np
import numba


@numba.njit
def _fill_scanline_jit(img_f, visited, labels, start_y, start_x, seed_color, tolerance_sq, label_id):
    H, W = img_f.shape[:2]
    # Numba-compatible queue implemented with a numpy array.
    queue = np.empty((H * W, 2), dtype=np.int32)
    q_head, q_tail = 0, 0

    queue[q_tail, 0] = start_x
    queue[q_tail, 1] = start_y
    q_tail += 1
    
    min_x, max_x = start_x, start_x
    min_y, max_y = start_y, start_y
    count = 0

    while q_head < q_tail:
        x, y = queue[q_head, 0], queue[q_head, 1]
        q_head += 1
        
        if visited[y, x]:
            continue
            
        # Find left boundary of span
        left = x
        while (left > 0 and 
               not visited[y, left - 1] and 
               np.dot(img_f[y, left - 1] - seed_color, img_f[y, left - 1] - seed_color) <= tolerance_sq):
            left -= 1
        
        # Find right boundary of span  
        right = x
        while (right < W - 1 and 
               not visited[y, right + 1] and 
               np.dot(img_f[y, right + 1] - seed_color, img_f[y, right + 1] - seed_color) <= tolerance_sq):
            right += 1
        
        # Fill the span
        labels[y, left:right + 1] = label_id
        visited[y, left:right + 1] = True
        
        # Update bounds and count
        min_x = min(min_x, left)
        max_x = max(max_x, right)  
        min_y = min(min_y, y)
        max_y = max(max_y, y)
        count += (right - left + 1)
        
        # Check adjacent lines for new spans
        for ny in [y - 1, y + 1]:
            if 0 <= ny < H:
                i = left
                while i <= right:
                    if (not visited[ny, i] and 
                        np.dot(img_f[ny, i] - seed_color, img_f[ny, i] - seed_color) <= tolerance_sq):
                        # Found start of new span
                        span_start = i
                        # Find end of span
                        while (i <= right and 
                               not visited[ny, i] and 
                               np.dot(img_f[ny, i] - seed_color, img_f[ny, i] - seed_color) <= tolerance_sq):
                            i += 1
                        # Add middle of span to queue to avoid redundant work
                        queue[q_tail, 0] = (span_start + i - 1) // 2
                        queue[q_tail, 1] = ny
                        q_tail += 1
                    else:
                        i += 1
    
    return min_x, min_y, max_x, max_y, count


def scanline_flood_fill_optimized(image, tolerance=10, min_area=100):
    """
    Optimized scanline flood fill segmentation for color images with tolerance.
    
    Args:
        image (np.ndarray): Input image (H, W, 3) in BGR or RGB
        tolerance (int): max color distance for connectivity
        min_area (int): minimum area to keep
    
    Returns:
        labels (np.ndarray): label image of same size as input
        regions (list): bounding boxes (x, y, w, h) of labeled regions
    """
    H, W = image.shape[:2]
    labels = np.zeros((H, W), dtype=np.int32)
    visited = np.zeros((H, W), dtype=bool)
    label_id = 1
    
    # Pre-compute squared tolerance for faster comparison
    tolerance_sq = tolerance * tolerance
    
    # Convert to float32 once
    img_f = image.astype(np.float32)
    
    regions = []
    
    # Process pixels in row-major order for better cache locality
    for y in range(H):
        for x in range(W):
            if not visited[y, x]:
                seed_color = img_f[y, x]
                min_x, min_y, max_x, max_y, count = _fill_scanline_jit(
                    img_f, visited, labels, y, x, seed_color, tolerance_sq, label_id)
                
                if count >= min_area:
                    regions.append((min_x, min_y, max_x - min_x + 1, max_y - min_y + 1))
                    label_id += 1
                else:
                    # Remove small region labels using vectorized operation
                    mask = labels == label_id
                    labels[mask] = 0
    
    return labels, regions


def draw_regions(image, regions):
    img = image.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    thickness = 1

    for idx, (x, y, w, h) in enumerate(regions, start=1):
        # Draw bounding box
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Prepare text
        text = str(idx)
        org = (x + 3, y + 15)

        # Draw black outline
        cv2.putText(img, text, org, font, font_scale, (0, 0, 0), thickness=3, lineType=cv2.LINE_AA)
        # Draw white fill
        cv2.putText(img, text, org, font, font_scale, (255, 255, 255), thickness=1, lineType=cv2.LINE_AA)

    return img


img = cv2.imread("masked.png")
labels, regions = scanline_flood_fill_optimized(img, tolerance=10, min_area=300)
annotated = draw_regions(img, regions)

cv2.imwrite("segment.png", annotated)