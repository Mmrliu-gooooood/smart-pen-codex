set -e
export PYTHONDONTWRITEBYTECODE=1 XDG_CONFIG_HOME=/tmp/servown/config XDG_CACHE_HOME=/tmp/servown/cache XDG_DATA_HOME=/tmp/servown/data
for mode in normal optimized; do
 flag=''; [ "$mode" = normal ] || flag=-O
 for i in 0 1 2 3; do /usr/bin/python3 $flag native_cut.py $i >own_cut_${mode}_${i}.log 2>&1; done
done
/usr/bin/python3 independent_replay.py >own_replay.log 2>&1
