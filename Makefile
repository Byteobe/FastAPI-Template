init:
	test -n "$(name)"
	rm -rf ./.git
	find ./ -type f -exec perl -pi -e 's/project_name/$(name)/g' *.* {} \;
	mv ./project_name ./$(name)
