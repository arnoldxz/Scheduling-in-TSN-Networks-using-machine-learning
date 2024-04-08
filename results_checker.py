from itertools import combinations

class ResultCheck:
    
    @staticmethod
    def to_transmission_sets(clean_offsets, frame_duration):
        transmission = []
        for frame in range(len(clean_offsets)):
            start = clean_offsets[frame]["Start"]
            end = start + frame_duration
            transmission.append((start, end))
        return transmission
    
    @staticmethod
    def overlap(set1, set2):
        # not (end1 < start2 or end2 < start1)
        return not (set1[1] <= set2[0] or set2[1] <= set1[0])
    
    @staticmethod
    def overlapping_check(clean_offsets, frame_duration):
        transmissions = ResultCheck.to_transmission_sets(clean_offsets, frame_duration)
        for combo in combinations(transmissions, r=2):
            set1 = combo[0]
            set2 = combo[1]
            if ResultCheck.overlap(set1, set2):
                print(f"Overlapping: {set1}--{set2}")
                return True
        return False

