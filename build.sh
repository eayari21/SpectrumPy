source bin/activate
pyinstaller src/IDEX-quicklook.py \
--onedir \
--windowed \
--icon impact.icns \
--name "SpectrumPY" \
--osx-bundle-identifier 'SPECTRUMPY_APP' \
--clean
