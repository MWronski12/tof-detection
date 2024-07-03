from typing import Tuple


def split_to_non_zero_sequences(samples: list[Tuple[int, int]]) -> list[list[Tuple[int, int]]]:
    result = []
    temp = []

    for i in range(len(samples)):
        if samples[i][1] == -1:
            if len(temp) > 0:
                result.append(temp)
                temp = []
        else:
            temp.append(samples[i])

    if len(temp) > 0:
        result.append(temp)

    return result


def split_to_monotonic_sequences(samples: list[Tuple[int, int]]) -> list[list[Tuple[int, int]]]:
    i = 0
    prev_direction = None
    result = []

    for j in range(1, len(samples)):

        direction = samples[j][1] > samples[i][1]

        if prev_direction == None:
            prev_direction = direction

        elif prev_direction != direction:
            result.append(samples[i:j])
            direction = None
            i = j

    if i < len(samples):
        result.append(samples[i:])

    return result


def split_to_non_zero_monotonic_series(samples: list[Tuple[int, int]], min_samples=0) -> list[list[Tuple[int, int]]]:

    def skip_to_next_motion(i) -> int:
        while i < len(samples) and samples[i][1] == -1:
            i += 1

        return i

    result = []
    prev_direction = None

    i = skip_to_next_motion(0)
    j = i + 1

    while j < len(samples):
        if samples[j][1] != -1:
            direction = samples[j][1] > samples[j - 1][1]

            if prev_direction == None:
                prev_direction = direction

            elif prev_direction != direction:
                series = samples[i:j]
                if len(series) >= min_samples:
                    result.append(series)

                prev_direction = None
                i = j

            j += 1

        elif samples[j][1] == -1:
            series = samples[i:j]
            if len(series) >= min_samples:
                result.append(series)

            prev_direction = None
            i = skip_to_next_motion(j)
            j = i + 1

    if i < len(samples):
        series = samples[i:]
        if len(series) >= min_samples:
            result.append(series)

    return result
