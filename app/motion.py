from monotonic_series import MonotonicSeries


class Motion:
    def __init__(self, series: list[MonotonicSeries], max_time_delta_ms: int) -> None:
        self._validate_series(series, max_time_delta_ms)
        series = self._filter_opposite_directions(series)
        self._monotonic_series = series

        self.num_series = len(series)
        self.num_samples_total = sum(len(series) for series in series)

        self.time_start = series[0].time_start
        self.time_end = series[-1].time_end
        self.time_total = self.time_end - self.time_start

        self.dist_start = series[0].dist_start
        self.dist_end = series[-1].dist_end
        self.dist_avg = sum(series.dist_avg for series in series) / len(series)

        self.direction = series[0].direction
        self.velocity = sum(series.velocity for series in series) / len(series)

    def _filter_opposite_directions(self, series: list[MonotonicSeries]) -> list[MonotonicSeries]:
        longest_series = max(series, key=lambda s: len(s))
        return [s for s in series if s.direction == longest_series.direction]

    def _validate_series(self, series: list[MonotonicSeries], max_time_delta_ms: int):
        assert len(series) > 0
        if not all(
            abs(series[i].time_start - series[i - 1].time_end) < max_time_delta_ms for i in range(1, len(series))
        ):
            print("Warning: time_delta invalid")
