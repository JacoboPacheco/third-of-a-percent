00000000000011e0 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii>:
    11e0:	test   %edx,%edx
    11e2:	jle    127e <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x9e>
    11e8:	mov    (%rsi),%rsi
    11eb:	mov    (%rdi),%rax
    11ee:	movslq %ecx,%rdi
    11f1:	mov    %edx,%r8d
    11f4:	mov    %r8d,%ecx
    11f7:	and    $0x3,%ecx
    11fa:	cmp    $0x4,%edx
    11fd:	jae    1203 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x23>
    11ff:	xor    %edx,%edx
    1201:	jmp    124f <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x6f>
    1203:	and    $0x7ffffffc,%r8d
    120a:	lea    (%rax,%rdi,4),%r9
    120e:	add    $0xc,%r9
    1212:	xor    %edx,%edx
    1214:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1220:	mov    (%rsi,%rdx,4),%r10d
    1224:	mov    %r10d,-0xc(%r9,%rdx,4)
    1229:	mov    0x4(%rsi,%rdx,4),%r10d
    122e:	mov    %r10d,-0x8(%r9,%rdx,4)
    1233:	mov    0x8(%rsi,%rdx,4),%r10d
    1238:	mov    %r10d,-0x4(%r9,%rdx,4)
    123d:	mov    0xc(%rsi,%rdx,4),%r10d
    1242:	mov    %r10d,(%r9,%rdx,4)
    1246:	add    $0x4,%rdx
    124a:	cmp    %rdx,%r8
    124d:	jne    1220 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x40>
    124f:	test   %rcx,%rcx
    1252:	je     127e <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x9e>
    1254:	shl    $0x2,%rdi
    1258:	lea    (%rdi,%rdx,4),%rdi
    125c:	add    %rdi,%rax
    125f:	lea    (%rsi,%rdx,4),%rdx
    1263:	xor    %esi,%esi
    1265:	data16 cs nopw 0x0(%rax,%rax,1)
    1270:	mov    (%rdx,%rsi,4),%edi
    1273:	mov    %edi,(%rax,%rsi,4)
    1276:	inc    %rsi
    1279:	cmp    %rsi,%rcx
    127c:	jne    1270 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x90>
    127e:	ret
    127f:	nop
