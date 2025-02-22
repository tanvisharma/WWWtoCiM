
# with open('regular-gemms.txt', 'w') as f:
#     f.write('Workload type\tM\tN\tK\t#MACs\tAlgorithmicReuse\n')
#     i = 16
#     while i <=8192:
#         macs = i*i*i
#         reuse = i/3 # i*i*i/(3*i*i)
#         f.write(f'regular-gemms\t{i}\t{i}\t{i}\t{macs}\t{reuse}\n')
#         i *= 2



# with open('all-gemms.txt', 'w') as f:
#     f.write('Workload type\tM\tN\tK\t#MACs\tAlgorithmicReuse\n')
#     for x in range(4, 14):
#         m = 2**x
#         for y in range(4, 14):
#             n = 2**y
#             for z in range(4, 14):
#                 k = 2**z
#                 macs = m*n*k
#                 reuse = m*n*k/(m*k + n*k + m*n)
#                 f.write(f'all-gemms\t{m}\t{n}\t{k}\t{macs}\t{reuse}\n')

for i in range(4,14):
    constant = 2**i
    filename = f"Mgemms-{constant}.txt"
    with open(filename, 'w') as f:
        f.write('Workload type\tM\tN\tK\t#MACs\tAlgorithmicReuse\n')
        k = 2**i
        n = 2**i
        for z in range(4, 14):
            m = 2**z
            macs = m*n*k
            reuse = m*n*k/(m*k + n*k + m*n)
            f.write(f'all-gemms\t{m}\t{n}\t{k}\t{macs}\t{reuse}\n')
