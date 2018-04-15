rrange = list(' 0123456789')
srange = [a + b + c + d 
	for a in rrange
	for b in rrange
	for c in rrange
	for d in rrange]

def make_str(pos, digit):
    s = list('    ')
    s[pos] = digit
    return ''.join(s)

 
srange = ['    '] + [
    make_str(pos, digit)
    for pos in [0, 1, 2, 3]
    for digit in list('0123456789')
]

def get_datas():
    datas = [(cmd, bus.read_byte_data(address, cmd)) for cmd in xrange(10)]
    print ' '.join('{}/{}'.format(cmd, bin(data)) for cmd, data in datas if data >0)

pos_to_cmd = {
  0: 0,
  1: 2,
  2: 6,
  3: 8,
  4: 4, # colon
}

val_array = [0]*11
for i, digit in enumerate(list('0123456789 ')):
    display.display(make_str(0, digit), False)
    time.sleep(0.1)
    val_array[i] = bus.read_byte_data(address, 0)
print val_array
	

pos_to_cmd = {
  0: 0,
  1: 2,
  2: 6,
  3: 8,
  4: 4, # colon
}
