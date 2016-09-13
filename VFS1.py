class BlockInfo:
  def __init__(self):
    self.size = 0

class VFS:
  def __init__(self):
    self.disk_1 = [bytearray(100) for i in range(200)]
    self.disk_2 = [bytearray(100) for i in range(300)]
    self.block_metadata = [BlockInfo() for i in range(500)]

  def write_block(self, block_no, block_info):
    if block_no > 500 or block_no < 1:
      raise "Invalid block no"
    if len(block_info) > 100:
      raise "Block data too big"
    metadata = self.block_metadata[block_no-1]
    metadata.size = len(block_info)
    metadata.free = False
    if block_no <= 200:
      block = self.disk_1[block_no-1]
    else:
      block = self.disk_2[block_no-201]
    block[:len(block_info)] = block_info

  def read_block(self, block_no, block_info):
    if block_no > 500 or block_no < 1:
      raise "Invalid block no"
    metadata = self.block_metadata[block_no-1]
    assert not metadata.free
    if block_no <= 200:
      block = self.disk_1[block_no-1]
    else:
      block = self.disk_2[block_no-201]
    res_size = min(len(block_info), metadata.size)
    block_info[:res_size] = block[:res_size]

def test_block_api():
  vfs = VFS()
  buff = bytearray(b'shubham')
  vfs.write_block(1, buff)
  rbuff1 = bytearray(10)
  rbuff2 = bytearray(2) # Test reading into small buffer.
  vfs.read_block(1, rbuff1)
  vfs.read_block(1, rbuff2)
  print(rbuff1.decode('utf-8'), rbuff2.decode('utf-8'))
  # Test data was copied and not referenced.
  print('Before: {1} {0}'.format(rbuff1[0], buff[0]))
  buff[0] = 69
  vfs.read_block(1, rbuff1)
  print('After: {1} {0}'.format(rbuff1[0], buff[0]))

  # Test writing to id > 200.
  buff = bytearray(b'shraw')
  vfs.write_block(300, buff)
  vfs.read_block(300, rbuff1)
  print(rbuff1.decode('utf-8'))

if __name__ == '__main__':
  test_block_api()