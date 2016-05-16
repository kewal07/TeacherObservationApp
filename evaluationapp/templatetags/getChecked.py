from django import template

register = template.Library()

@register.filter(name='getChecked')
def getChecked(boolVal):
	ret = ""
	if boolVal:
		ret = "checked"
	return ret

@register.filter(name='getDisabled')
def getDisabled(v):
	ret = ""
	if v:
		ret = "disabled"
	return ret

@register.filter(name='getCheckedList')
def getCheckedList(v1, v2):
	print("v1",v1,"v2",v2)
	ret = ""
	if v1 in v2:
		ret = "checked"
	return ret

@register.filter(name='getCheckedStr')
def getCheckedStr(v1, v2):
	print("v1",v1,"v2",v2)
	ret = ""
	if v1 == v2:
		ret = "checked"
	return ret

@register.filter(name='getSelectedSection')
def getSelectedSection(val,totalVal):
	ret = ""
	if int(val) == int(totalVal):
		ret = "selected"
	return ret

@register.filter(name='getSelected')
def getSelected(val,totalVal):
	print("1",val,"2",totalVal)
	ret = ""
	if (val) == (totalVal):
		ret = "selected"
	return ret