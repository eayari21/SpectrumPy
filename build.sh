source bin/activate
pyinstaller src/IDEX-quicklook.py \
--onefile \
--windowed \
--icon impact.icns \
--name "SpectrumPY" \
--osx-bundle-identifier 'SPECTRUMPY_APP' \
--hidden-import sqlalchemy \
--clean
