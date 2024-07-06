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



