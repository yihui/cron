install.packages('xfun', repos = 'https://yihui.r-universe.dev')

if (dir.exists('package')) xfun::in_dir('package', {
  # release this package
  xfun:::install_deps()
  xfun::pkg_load2('curl')
  x = xfun::read_utf8(f <- 'DESCRIPTION')
  i = grep('^Version: ', x)
  v = sub('^Version: (\\d+\\.\\d+).*', '\\1', x[i])
  v = as.integer(strsplit(v, '.', fixed = TRUE)[[1]])
  v[2] = v[2] + 1
  v = paste(v, collapse = '.')
  x[i] = paste('Version:', v)
  xfun::write_utf8(x, f)
  xfun::install_dir('.', build = FALSE)
  p = xfun:::pkg_build()
  # when CRAN submission is closed, keep trying
  resp = curlGetHeaders('https://xmpalantir.wu.ac.at/cransubmit/index2.php')
  if (any(startsWith(resp, 'Location: index.php?strErr=1'))) {
    xfun::retry(xfun::submit_cran, p, .times = 30, .pause = 600)
  } else xfun::submit_cran(p)
}) else {
  # check which packages are too old and need new releases
  pkgs = xfun:::cran_updatable(30, 'Yihui Xie')
  pkgs = setdiff(pkgs, 'rolldown')  # ignore rolldown
  if (length(pkgs) > 0) stop(paste(c(
    paste(c('Packages need to be updated:', pkgs), collapse = ' '),
    sprintf('https://cloud.r-project.org/package=%s', pkgs)
  ), collapse = '\n'))
}
