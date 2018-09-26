def build_requires(spec):
    brs = spec.build_requires
    for pkg in spec.packages:
        pkg_brs = getattr(pkg, 'build_requires', [])
        if pkg_brs:
            brs += pkg_brs
    return brs
