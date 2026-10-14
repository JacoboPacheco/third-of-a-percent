0000000000001220 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE>:
    1220:	mov    (%rdi),%rdx
    1223:	mov    0x8(%rdi),%rsi
    1227:	sub    %rdx,%rsi
    122a:	je     1241 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x21>
    122c:	sar    $0x2,%rsi
    1230:	mov    %esi,%ecx
    1232:	and    $0x7,%ecx
    1235:	cmp    $0x8,%rsi
    1239:	jae    1244 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x24>
    123b:	xor    %edi,%edi
    123d:	xor    %eax,%eax
    123f:	jmp    1298 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x78>
    1241:	xor    %eax,%eax
    1243:	ret
    1244:	and    $0xfffffffffffffff8,%rsi
    1248:	xor    %edi,%edi
    124a:	xor    %eax,%eax
    124c:	nopl   0x0(%rax)
    1250:	movslq (%rdx,%rdi,4),%r8
    1254:	add    %rax,%r8
    1257:	movslq 0x4(%rdx,%rdi,4),%rax
    125c:	movslq 0x8(%rdx,%rdi,4),%r9
    1261:	add    %rax,%r9
    1264:	add    %r8,%r9
    1267:	movslq 0xc(%rdx,%rdi,4),%rax
    126c:	movslq 0x10(%rdx,%rdi,4),%r8
    1271:	add    %rax,%r8
    1274:	movslq 0x14(%rdx,%rdi,4),%r10
    1279:	add    %r8,%r10
    127c:	add    %r9,%r10
    127f:	movslq 0x18(%rdx,%rdi,4),%r8
    1284:	movslq 0x1c(%rdx,%rdi,4),%rax
    1289:	add    %r8,%rax
    128c:	add    %r10,%rax
    128f:	add    $0x8,%rdi
    1293:	cmp    %rdi,%rsi
    1296:	jne    1250 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x30>
    1298:	test   %rcx,%rcx
    129b:	je     12bf <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x9f>
    129d:	lea    (%rdx,%rdi,4),%rdx
    12a1:	xor    %esi,%esi
    12a3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b0:	movslq (%rdx,%rsi,4),%rdi
    12b4:	add    %rdi,%rax
    12b7:	inc    %rsi
    12ba:	cmp    %rsi,%rcx
    12bd:	jne    12b0 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x90>
    12bf:	ret
