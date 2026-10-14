0000000000001220 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE>:
    1220:	mov    (%rdi),%rdx
    1223:	mov    0x8(%rdi),%rax
    1227:	sub    %rdx,%rax
    122a:	je     124c <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x2c>
    122c:	sar    $0x2,%rax
    1230:	cmp    $0x1,%rax
    1234:	mov    %rax,%rdi
    1237:	adc    $0x0,%rdi
    123b:	mov    %edi,%ecx
    123d:	and    $0x7,%ecx
    1240:	cmp    $0x8,%rax
    1244:	jae    124f <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x2f>
    1246:	xor    %esi,%esi
    1248:	xor    %eax,%eax
    124a:	jmp    12a8 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x88>
    124c:	xor    %eax,%eax
    124e:	ret
    124f:	and    $0xfffffffffffffff8,%rdi
    1253:	xor    %esi,%esi
    1255:	xor    %eax,%eax
    1257:	nopw   0x0(%rax,%rax,1)
    1260:	movslq (%rdx,%rsi,4),%r8
    1264:	add    %rax,%r8
    1267:	movslq 0x4(%rdx,%rsi,4),%rax
    126c:	movslq 0x8(%rdx,%rsi,4),%r9
    1271:	add    %rax,%r9
    1274:	add    %r8,%r9
    1277:	movslq 0xc(%rdx,%rsi,4),%rax
    127c:	movslq 0x10(%rdx,%rsi,4),%r8
    1281:	add    %rax,%r8
    1284:	movslq 0x14(%rdx,%rsi,4),%r10
    1289:	add    %r8,%r10
    128c:	add    %r9,%r10
    128f:	movslq 0x18(%rdx,%rsi,4),%r8
    1294:	movslq 0x1c(%rdx,%rsi,4),%rax
    1299:	add    %r8,%rax
    129c:	add    %r10,%rax
    129f:	add    $0x8,%rsi
    12a3:	cmp    %rsi,%rdi
    12a6:	jne    1260 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x40>
    12a8:	test   %rcx,%rcx
    12ab:	je     12cf <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xaf>
    12ad:	lea    (%rdx,%rsi,4),%rdx
    12b1:	xor    %esi,%esi
    12b3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12c0:	movslq (%rdx,%rsi,4),%rdi
    12c4:	add    %rdi,%rax
    12c7:	inc    %rsi
    12ca:	cmp    %rsi,%rcx
    12cd:	jne    12c0 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xa0>
    12cf:	ret
