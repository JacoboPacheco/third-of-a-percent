0000000000001220 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rdi),%rax
    1223:	mov    0x8(%rdi),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     1274 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x54>
    122c:	sar    $0x2,%rcx
    1230:	mov    (%rsi),%rdx
    1233:	mov    0x8(%rsi),%rsi
    1237:	sub    %rdx,%rsi
    123a:	sar    $0x2,%rsi
    123e:	cmp    $0x1,%rcx
    1242:	adc    $0x0,%rcx
    1246:	xor    %edi,%edi
    1248:	nopl   0x0(%rax,%rax,1)
    1250:	cmp    %rsi,%rdi
    1253:	jae    1275 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x55>
    1255:	lea    0x1(%rdi),%r8
    1259:	cmp    %rsi,%r8
    125c:	jae    1275 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x55>
    125e:	mov    0x4(%rdx,%rdi,4),%r8d
    1263:	add    (%rdx,%rdi,4),%r8d
    1267:	mov    %r8d,(%rax,%rdi,2)
    126b:	add    $0x2,%rdi
    126f:	dec    %rcx
    1272:	jne    1250 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>
    1274:	ret
    1275:	ud2
    1277:	nopw   0x0(%rax,%rax,1)
