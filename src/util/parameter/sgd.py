import egraph as eg


class SGDParameter:
    def __init__(self, *, iterator: int, eps: float, seed: int | None = None) -> None:
        self.iter = iterator
        self.eps = eps
        self.seed = seed
        self.rng = eg.Rng.seed_from(seed) if seed is not None else eg.Rng()
