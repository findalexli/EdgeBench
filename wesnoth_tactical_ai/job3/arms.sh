# Clean repeat: community21-wesnoth-qwen38's local old image build failed on a mirror error, so its old judge's identity isn't recorded. Stop unless both images were built here.
docker image inspect $IMGOLD --format '{{.Id}}' >$O/d/img-old.txt 2>&1 || { echo "NO-OLD-IMAGE" >>$O/summary.txt; exit 6; }
docker image inspect $IMGNEW --format '{{.Id}}' >$O/d/img-new.txt 2>&1 || { echo "NO-NEW-IMAGE" >>$O/summary.txt; exit 6; }
for x in "old $IMGOLD" "new $IMGNEW"; do set -- $x; sh /job/subs/diagnose.sh $2 /job/subs/qwen38.tar.gz >$O/d/diag-$1-qwen38.txt 2>&1; echo "diag $1 rc=$?" >>$O/summary.txt; done
for r in 11 12 13 14; do o="old new"; [ $(( r%2 )) = 0 ] && o="new old"; for sd in $o; do seval qwen38-$r $sd qwen38.tar.gz 260; done; done
