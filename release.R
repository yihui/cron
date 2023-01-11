install.packages('xfun', repos = 'https://yihui.r-universe.dev')

pkgs = xfun:::cran_updatable(30, 'Yihui Xie')
pkgs = setdiff(pkgs, 'rolldown')  # ignore rolldown
if (length(pkgs) > 0) stop(
  paste(sprintf('https://cran.rstudio.com/package=%s', pkgs), collapse = '\n')
)
