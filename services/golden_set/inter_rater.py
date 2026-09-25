def should_trigger_inter_rater(labeled_count: int) -> bool:
    # Trigger at 4, then every 6 after
    if labeled_count == 4:
        return True
    if labeled_count >= 10 and (labeled_count - 4) % 6 == 0:
        return True
    return False
