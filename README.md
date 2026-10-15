# earth-data

Cached Earth reference data for procgen_world (`tools/earth_data.py`), kept off `main` because it is binary and git-ignored there (`data/`).

- `raw_*.npz`: downloads (ETOPO1 bed and ice, Kottek Köppen, GPCC and GPCP rain, NCEP temperature and cloud, ICOADS cloud, CRU sunshine, Ramankutty-Foley potential vegetation), as fetched by `tools/earth_data.py`. Some of the source servers are slow or flaky, hence the cache.
- `L6.npz`, `L7.npz`, `clouds_L6.npz`, `potveg_L6.npz`: those fields sampled onto the model grids. They're rebuilt from the raw files if missing.

Restore into a checkout of `main` without staging anything:

```sh
git fetch origin earth-data
git restore --source=origin/earth-data --worktree -- data/earth
```
