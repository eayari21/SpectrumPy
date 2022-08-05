source bin/activate
pyinstaller src/windows-qt.py -F \
--windowed \
--icon impact.icns \
--name "SpectrumPY" \
--osx-bundle-identifier 'SPECTRUMPY_APP' \
--clean
