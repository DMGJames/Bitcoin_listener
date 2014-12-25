if [ "$LD_LIBRARY_PATH" ]; then
  export LD_LIBRARY_PATH=/usr/local/lib:"$LD_LIBRARY_PATH"
else
  export LD_LIBRARY_PATH=/usr/local/lib
fi
